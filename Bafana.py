from tempfile import SpooledTemporaryFile
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import numpy as np
import queue
import threading
import atexit
import random
import time
global IP
global PORT_FROM_MAX
global PORT_TO_MAX
IP = "127.0.0.1"
PORT_FROM_MAX = 5007
PORT_TO_MAX = 5010

def motifRecognition(notes,motifs):
    similarity = np.empty(4)
    i = 0
    for motif in motifs:
        currentarray = np.array(motif[0])
        difference = np.subtract(notes,currentarray)
        np.append(similarity,np.sum(np.absolute(difference)))
    result = np.argmin(similarity)
    return result

def delayT(tElapse,motif):
    sectiont = motif[1][0]
    totalT = motif[1][1]
    ratio = tElapse/sectiont
    delayToEnd =  (ratio*totalT) - tElapse
    speed = 1024/ratio #1024 is 1X speed
    return [speed,delayToEnd]



def bafana(name, *args):
    receivednotes = np.sum(np.array(list(args)))
    motifnum = int(receivednotes)
    if motifnum > 1:
        lastsection.put(motifnum)
        print("endsection",motifnum)
        delayTnew = float((newTempMotif[motifnum][1][1] - newTempMotif[motifnum][1][0])/1000)
        time.sleep(delayTnew)
        tempo = float(speedF)
        client.send_message("/play", [motifnum,tempo])
        lastsection.put(motifnum)
        timetoRepeatagain = random.randint(2,3)
        for i in range(timetoRepeatagain):
            client.send_message("/play", [motifnum,speedF])
            time.sleep(newTempMotif[motifnum][1][1]/1000)
        

    else:
        motifq.put(motifnum)



def test(name,*args):
    totalt = np.sum(np.array(list(args)))
    timeq.put(totalt)


# OSC Listening
global timeq
global pieceq
global listen
global lastsection
timeq = queue.Queue()
motifq = queue.Queue()
liten = queue.Queue()
lastsection = queue.Queue()

motif1 = [[60,64,65],[3000,8000]]
motif2 = [[60,60,64],[3124,10000]] #3062
motif4 = [[59,55,59],[2062,10124]]
motif3 = [[60,63,65],[2124,9000]]

global motifList
motifList =[motif1,motif2,motif3,motif4]

global dispatcher
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/filter", bafana)
dispatcher.map("/filter2", test)

# server = osc_server.ThreadingOSCUDPServer((IP, PORT_FROM_MAX), dispatcher)
# print("Serving on {}".format(server.server_address))
# server.serve_forever()

def server():
    server = osc_server.ThreadingOSCUDPServer((IP, PORT_FROM_MAX), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
    atexit.register(server.server_close())

# Turn-on the worker thread.
threading.Thread(target=server, daemon=True).start()
global client
client = udp_client.SimpleUDPClient(IP, PORT_TO_MAX)

print("test")

## PArt 1.1
#start by listening to first motif
client.send_message("/listen", 1)
print("sent")
current = int(motifq.get())
ttime = timeq.get()
currentmotif = motifList[current]
[speed,delayToEnd] = delayT(ttime,currentmotif)
speed = float(speed)
timetoRepeat =random.randint(0, 3)
#we found the motif so wait to play it
time.sleep(delayToEnd/1000)
print(current,speed)
client.send_message("/play", [current,speed])

delaytoEndpt1 = float((ttime/currentmotif[1][0])*(currentmotif[1][1])/1000)
print(delaytoEndpt1)
time.sleep(delaytoEndpt1)
i=0
#play it a couple times
for i in range(timetoRepeat):
    client.send_message("/play", [current,speed])
    print("again",delaytoEndpt1)
    time.sleep(delaytoEndpt1)
    print("again2")
print("done")

## Part 1.2
time.sleep(3)
print("next part")
client.send_message("/play", [current,speed])
time.sleep(delaytoEndpt1)

##Part 1.3
# listen to new motif 
client.send_message("/listen", 1)
print("sent")
current = int(motifq.get())
ttime = float(timeq.get())
currentmotif = motifList[current]
[speed,delayToEnd] = delayT(ttime,currentmotif)
global speedF
speedF = float(speed)
#this speed is the the final speed for the rest of the piece
#Lets calculate the correct times to wait for each motif
ratio = ttime/currentmotif[1][0]
global newTempMotif
newTempMotif = motifList
i=0
for motif in motifList:
    newTempMotif[i][1][1] = float(ratio*motif[1][1])
    newTempMotif[i][1][0] = float(ratio*motif[1][0])
    i += 1


#Now we can use this as a delaytoend

timetoRepeat =random.randint(2, 3)
# we found the motif so wait to play it
time.sleep(delayToEnd/1000)
client.send_message("/play", [current,speed])
delaytoEnd2 = float((ttime/currentmotif[1][0])*(currentmotif[1][1]/1000))
i=0
#play it a couple times
for i in range(timetoRepeat):
    client.send_message("/play", [current,speed])
    time.sleep(delaytoEnd2)

client.send_message("/listen2", 1)
print("damn we made it")
while lastsection.empty() == True:
    whattodo = random.randint(0,2)
    currentmotif = newTempMotif[whattodo]
    if whattodo < 2:
        print("play!",whattodo)
        client.send_message("/play", [whattodo,speed])
        
    else:
        whattodo = 1
        print("waiting")
    delayToEnd = float(newTempMotif[whattodo][1][1]/1000)
    time.sleep(delayToEnd)

print("uh oh")


lastsection.get()
print("what now")
input("wait?????")
currentmot = lastsection.get()
delayToEnd = newTempMotif[currentmot][1][1]
time.sleep(delayToEnd)















# See PyCharm help at https://www.jetbrains.com/help/pycharm/
