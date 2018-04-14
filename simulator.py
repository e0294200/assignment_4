'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def sum_burst_time(process_list):
    sum_burst_time = 0
    for process in process_list:
        sum_burst_time = sum_burst_time + process.burst_time
    return sum_burst_time

def find_shortest_burst_time(process_list):
    shortest_id = -1
    shortest_burst_time = sys.maxint
    for id in xrange(0,len(process_list)):
        if process_list[id].burst_time == 0:
            continue
        if process_list[id].burst_time < shortest_burst_time:
            shortest_burst_time = process_list[id].burst_time
            shortest_id = id
    return shortest_id

def find_earliest_arrive_time(process_list):
    earliest_arrive_time = sys.maxint
    for id in xrange(0,len(process_list)):
        #Only consider processes with remaining burst_time
        if process_list[id].burst_time == 0:
            continue
        if process_list[id].arrive_time < earliest_arrive_time:
            earliest_arrive_time = process_list[id].arrive_time
    return earliest_arrive_time

def find_process_with_earliest_arrive_time(process_list):
    earliest_arrive_time = sys.maxint
    process = 0
    for id in xrange(0,len(process_list)):
        #Only consider processes with remaining burst_time
        if process_list[id].burst_time == 0:
            continue
        if process_list[id].arrive_time < earliest_arrive_time:
            earliest_arrive_time = process_list[id].arrive_time
            process = process_list[id]
    return process

def count_processes_with_non_zero_burst_time(process_list):
    count = 0
    for id in xrange(0,len(process_list)):
        if process_list[id].burst_time != 0:
            count = count + 1
    return count

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list_input, time_quantum ):
    schedule = []
    current_time = 0
    current_id = 0
    waiting_time = 0
    missed_arrive_time_count = 0
    process_list = copy.deepcopy(process_list_input)
    
    #Keep looping through the process_list till each process' burst_time has been reduced to 0
    while sum_burst_time(process_list):
        
        #Check if current process has any more burst_time left
        if process_list[current_id].burst_time > 0:
            #Check if it is time to run the current process
            if current_time >= process_list[current_id].arrive_time:
                missed_arrive_time_count = 0

                schedule.append((current_time,process_list[current_id].id))

                #HACK: arrive_time will be changed later to keep track of end time of process' time slot
                waiting_time = waiting_time + (current_time - process_list[current_id].arrive_time)

##                print "===== current_id", current_id, "current_time", current_time, "waiting_time", waiting_time
##                for process in process_list:
##                    print process
                    
                #Run this process for time_quantum units
                if process_list[current_id].burst_time < time_quantum:
                    current_time = current_time + process_list[current_id].burst_time
                    process_list[current_id].burst_time = 0
                else:
                    current_time = current_time + time_quantum
                    process_list[current_id].burst_time = process_list[current_id].burst_time - time_quantum

                #HACK: Dual-use arrive_time to keep track of end time of process' time slot
                process_list[current_id].arrive_time = current_time

            else:
                missed_arrive_time_count = missed_arrive_time_count + 1
                if missed_arrive_time_count == count_processes_with_non_zero_burst_time(process_list):
                    #Artifically advance current_time to earliest arrive_time of all processes with burst_time
                    #This happens when we have looped through all items in process_list, and cannot find
                    #a process to run.
                    current_time = find_earliest_arrive_time(process_list)
                
        current_id = (current_id + 1) % len(process_list)
        
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SRTF_scheduling(process_list_input):
    schedule = []
    current_time = 0
    run_id = -1
    prev_run_id = 0
    waiting_time = 0
    process_list = copy.deepcopy(process_list_input)

    #Trigger a check whenever a process arrives (will not trigger for last process)
    for arrive_id in xrange(0,len(process_list)-1):
        current_time = process_list[arrive_id].arrive_time

        #Since we already know the future (cheating), let's calculate how much time before the next process arrives
        time_remaining = process_list[arrive_id+1].arrive_time - process_list[arrive_id].arrive_time

        while time_remaining > 0:
        
            #Find the process with the shortest burst time, from sub-list of processes that have already arrived
            prev_run_id = run_id
            run_id = find_shortest_burst_time(process_list[0:arrive_id+1])

##            print "===== arrive_id", arrive_id, "current_time", current_time, "time_remaining", time_remaining, "run_id", run_id

            if run_id == -1:
                #No suitable processes found, just wait for next process to arrive
                break

            if prev_run_id != run_id:
                waiting_time = waiting_time + (current_time - process_list[run_id].arrive_time)
##                print "===== waiting_time", waiting_time

            if time_remaining > process_list[run_id].burst_time:
                #There is time to complete this process.
                #After completing, we can look for more processes in the next iteration of the while loop
                if prev_run_id != run_id:
                    schedule.append((current_time,process_list[run_id].id))
                process_list[run_id].arrive_time = current_time + process_list[run_id].burst_time
                current_time = current_time + process_list[run_id].burst_time
                time_remaining = time_remaining - process_list[run_id].burst_time
                process_list[run_id].burst_time = 0
            else:
                #There is not enough time
                #Exit while loop
                if prev_run_id != run_id:
                    schedule.append((current_time,process_list[run_id].id))
                process_list[run_id].burst_time = process_list[run_id].burst_time - time_remaining
                process_list[run_id].arrive_time = current_time + time_remaining
                time_remaining = 0
            
##        for process in process_list:
##            print process

    #Set current_time to time when last process arrives
    current_time = process_list[len(process_list)-1].arrive_time
    
    #All processes have arrived. Now run the processes in order of shortest burst time
    prev_run_id = run_id
    run_id = find_shortest_burst_time(process_list) 
    while run_id != -1:
        schedule.append((current_time,process_list[run_id].id))
        
##        print "===== run_id", run_id, "current_time", current_time, "waiting_time", waiting_time
##        for process in process_list:
##            print process

        if prev_run_id != run_id:
            waiting_time = waiting_time + (current_time - process_list[run_id].arrive_time)
        
        current_time = current_time + process_list[run_id].burst_time
        process_list[run_id].burst_time = 0

##        print "===== run_id", run_id, "current_time", current_time, "waiting_time", waiting_time
##        for process in process_list:
##            print process

        prev_run_id = run_id
        run_id = find_shortest_burst_time(process_list)

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SJF_scheduling(process_list_input, alpha):
    schedule = []
    current_time = 0
    current_id = 0
    waiting_time = 0
    predicted_burst_times = dict()
    initial_prediction = 5
    process_list = copy.deepcopy(process_list_input)

    #Initialize with first process in process_list
    arrived_processes_list = [process_list[0]]
    predicted_burst_times[process_list[0].id] = initial_prediction

    while len(arrived_processes_list) != 0:
##        print "===== predicted_burst_times"
##        for id in predicted_burst_times.iterkeys():
##            print "     id", id, "predicted_burst_time", predicted_burst_times[id]
            
        #Find out which process has the shortest remaining predicted burst time
        id_with_shortest_burst_time = -1 
        shortest_burst_time = sys.maxint
        for arrived_process in arrived_processes_list:
            #Ignore processes with ids that match the current id_with_shortest_burst_time
            if arrived_process.id != id_with_shortest_burst_time:
                if predicted_burst_times[arrived_process.id] < shortest_burst_time:
                    shortest_burst_time = predicted_burst_times[arrived_process.id]
                    id_with_shortest_burst_time = arrived_process.id

        #Find first task in arrived_processes_list that has id matching id_with_shortest_burst_time
        process_to_run = -1
        for arrived_process in arrived_processes_list:
            if arrived_process.id == id_with_shortest_burst_time:
                process_to_run = arrived_process
                break

        if process_to_run == -1:
            print "[!] Cannot find id_with_shortest_burst_time", id_with_shortest_burst_time, " in arrived_processes_list!"
            raise
        
##        print "===== current time", current_time, "id_with_shortest_burst_time", id_with_shortest_burst_time, "process_to_run", process_to_run

        #'Run' the process with the shortest remaining predicted burst time
        schedule.append((current_time,process_to_run.id))
        waiting_time = waiting_time + (current_time - process_to_run.arrive_time)
        current_time = current_time + process_to_run.burst_time

        #Recalculate predicted burst time for this process id
        predicted_burst_times[process_to_run.id] = process_to_run.burst_time*alpha + (1-alpha)*predicted_burst_times[process_to_run.id]
        
        #Remove the run process from the process_list and arrived_processes_list
        arrived_processes_list.remove(process_to_run)
        process_list.remove(process_to_run)

        #Look for processes that have arrived while process_to_run was running
        for process in process_list:
            if process.arrive_time <= current_time:
                if process not in arrived_processes_list:
                    arrived_processes_list.append(process)
                    #If this is the first time seeing this process id, initialize its predicted burst time
                    if process.id not in predicted_burst_times:
                        predicted_burst_times[process.id] = initial_prediction

        #If no processes were added to the arrived_processes_list, check if there are other processes in
        #process_list, and advance current_time to the next earliest arrive_time
        if len(arrived_processes_list) == 0:
            if len(process_list) != 0:
                process = find_process_with_earliest_arrive_time(process_list)
                if process != 0:
                    arrived_processes_list.append(process)
                    #If this is the first time seeing this process id, initialize its predicted burst time
                    if process.id not in predicted_burst_times:
                        predicted_burst_times[id] = initial_prediction
                    current_time = process.arrive_time
                
##        print "===== arrived_processes_list"
##        for arrived_process in arrived_processes_list:
##            print "    ", arrived_process
    
    average_waiting_time = waiting_time/float(len(process_list_input))
    return schedule, average_waiting_time


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])
