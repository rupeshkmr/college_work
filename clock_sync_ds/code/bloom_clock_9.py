# referenced from https://towardsdatascience.com/understanding-lamport-timestamps-with-pythons-multiprocessing-library-12a6427881c6
from multiprocessing import Process,Pipe,Manager
from os import getpid
from datetime import datetime
from bloom_filter import BloomFilter
from hasse import Hasse
import json
import csv
n = 20#number of items_count
p = 0.29 # False positive probability
t = [0,0,0,0]# to store the global timestamp for each process

#Helper Functions
#Print Local timestamp and actual time on machine executing the processes
def local_time(counter):
    return counter

#Calculate new timestamp when a process receives a msg
def calc_recv_timestamp(eid,recv_time_stamp, counter):
    counter.update_filter(eid,recv_time_stamp)
    return counter
#prints all the previous timestamps for a particular process
def print_history(counter,pid):
    print("Displaying histories of process pid = ",pid)
    for i in counter.history.keys():
        print(i,":\t",counter.history[i])








#Function for every event that ma occur 1: Local event 2: Message send 3: Message Received
#The event function will return updated timestamp

#1 Local event
#Input is local counter and process id
#return local_timestamp +1
#eid is the event id string name
def event(pid,counter,eid):
    global t,poset1
    t[pid] += 1
    #print('{} Event happened in {} !'.format(eid,pid))
    #print("Ip filter\t:",counter.bit_array)
    counter.add(eid)

    #print("Op filter\t:",counter.bit_array)
    #poset1[eid] = counter.bit_array
    data = {eid:counter.bit_array}
    with open('bloom_poset_9.txt', 'a') as outfile:
        json.dump(data, outfile)
        outfile.write("\n")
    return counter

#2 Message send
#Requires pid ,counter and a pipe for two way communication
#pipe creates two objects one for send and one for receive
#it sends down it's updated counter alongwith the message in the pipe
def send_message(pipe,pid,counter,eid):
    global t,poset1
    t[pid]+=1
    #print('Message sent from  ' +str(pid)+" event id "+eid)
    #print("Ip filter\t:",counter.bit_array)
    counter.add(eid)
    #print("Op filter\t:",counter.bit_array)
    #poset1[eid] = counter.bit_array
    data = {eid:counter.bit_array}
    with open('bloom_poset_9.txt', 'a') as outfile:
        json.dump(data, outfile)
        outfile.write("\n")   
    pipe.send((eid,counter))
    
    # #print(counter.bit_array)
    return counter

#3 Message Receive
#receives message, timestamp by invoking recv function on pipe
#Then it further calculates it's new timestamp depending upon the received timestamp and current timestamp
def recv_message(pipe,pid,counter,eid):
    global t,poset1
    t[pid]+=1
    #print('Message received at '+ str(pid)+"event id "+eid)
    #print("Ip filter\t:",counter.bit_array)
    #counter.add(eid)
    message,timestamp = pipe.recv(); 
    #print("\tfrom: "+message+"  timestamp\t:",end="")
    #print(timestamp.bit_array)
    counter = calc_recv_timestamp(eid,timestamp,counter)
    #print("Op filter\t:",counter.bit_array)
    #poset1[eid] = counter.bit_array
    data = {eid:counter.bit_array}
    with open('bloom_poset_9.txt', 'a') as outfile:
        json.dump(data, outfile)
        outfile.write("\n")
    # #print(counter.bit_array)
    return counter

#Defenitions for three processes
#Each process starts with getting it's process id and sets it's counter to 0



def process_one(pipe13,pipe14):
    pid = 0
    counter = BloomFilter(n,p,0)
    counter = event(pid,counter,'a')
    counter = recv_message(pipe14,pid,counter,'b')
    
    
def process_two(pipe23):
    pid = 1
    counter = BloomFilter(n,p,0)
    counter = send_message(pipe23,pid,counter,'c')
    counter = event(pid,counter,'d')
    counter = send_message(pipe23,pid,counter,'e')
    
def process_three(pipe31,pipe32):
    pid = 2
    counter = BloomFilter(n,p,0)
    counter = event(pid,counter,'f')
    counter = recv_message(pipe32,pid,counter,'g')
    counter = recv_message(pipe32,pid,counter,'h')
    
def process_four(pipe41):
    pid = 3
    counter = BloomFilter(n,p,0)
    counter = send_message(pipe41,pid,counter,'i')
    counter = event(pid,counter,'j')
   


def get_ordering(poset):

    #print(poset)
    
    hasse = Hasse(poset)
    #hasse.print_table()
    print(hasse.hasse)
    with open('vector_poset.csv','a') as openfile:
        csvwriter = csv.writer(openfile,delimiter=',')
        for i in hasse.table:
            csvwriter.writerow(i)
if __name__ == '__main__':
    
    #oneandtwo, twoandone = Pipe()
    twoandthree, threeandtwo = Pipe()
    oneandthree, threeandone = Pipe()
    oneandfour, fourandone = Pipe()
    process1 = Process(target=process_one,args=(oneandthree,oneandfour))
    process2 = Process(target=process_two,args=(twoandthree,))
    process3 = Process(target=process_three,args=(threeandone,threeandtwo))
    process4 = Process(target=process_four,args=(fourandone,))

    process1.start()
    process2.start()
    process3.start()
    process4.start()

    process1.join()
    process2.join()
    process3.join()
    process4.join()
    
    poset = {}
    with open('bloom_poset_9.txt') as json_file:
        for jsonobj in json_file:
            data = json.loads(jsonobj)#[json.load(line) for line in json_file]
            poset[list(data.keys())[0]] = data[list(data.keys())[0]]
    get_ordering(poset)
    ##print(poset)
    
