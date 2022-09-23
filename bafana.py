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
global ShimonDelay
ShimonDelay = 0.50

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
        time.sleep(float(delayTnew-ShimonDelay))
        tempo = float(speedF)
        client.send_message("/inter", 1)
        client.send_message("/play", [motifnum,tempo])
        timetoRepeatagain = random.randint(2,3)
        for i in range(timetoRepeatagain):
            client.send_message("/play", [motifnum,speedF])
            time.sleep(newTempMotif[motifnum][1][1]/1000)
        lastsection.put(motifnum)  
    else:
        motifq.put(motifnum)



def test(name,*args):
    totalt = np.sum(np.array(list(args)))
    timeq.put(totalt)


def follow(name, *args):
    receivednotes = np.array(list(args))
    if sum(receivednotes) > 30:
        if sum(receivednotes) < 100:
            motif = 6

        else:
            motif = 0
            # lastsection.put(2)
        send = int(motif)
        delayTnew = float((newTempMotif[motif][1][1] - newTempMotif[motif][1][0])/1000)
        time.sleep(float(delayTnew-ShimonDelay))
        if motif == 0:
            client.send_message("/endsong", 0)
        client.send_message("/inter", 1)
        tempo = float(speedF)
        client.send_message("/play", [send,tempo])
        time.sleep(newTempMotif[motif][1][1]/1000)
        client.send_message("/play", [send,tempo])
        time.sleep(newTempMotif[motif][1][1]/1000)
        lastsection.put(2)
        

        
    else:
        motifswapper.put(receivednotes)



def section3(name, *args):
    print('s3swap')
    motif = np.sum(np.array(list(args)))
    if motif > 5:
        if motif == 6:
            lastsection.put(2)
            
            delayTnew = float((newTempMotif[motif][1][1] - newTempMotif[motif][1][0])/1000)
            time.sleep(float(delayTnew-ShimonDelay))
            tempo = float(speedF)
            client.send_message("/inter", 1)
            send = int(motif)
            client.send_message("/play", [send,tempo])
            time.sleep(newTempMotif[motif][1][1]/1000)
            lastsection.put(2)
        else:
            motiftosend = 7

    if (motif%2) == 0:
        motiftosend = int(motif)
    else:
        motiftosend = int(motif-1)
    motifswapper.put(motiftosend)




# OSC Listening
global timeq
global pieceq
global listen
global lastsection
timeq = queue.Queue()
motifq = queue.Queue()
liten = queue.Queue()
lastsection = queue.Queue()
motifswapper = queue.Queue()
ending = queue.Queue()
# midi BPM is 120
motif1 = [[60,64,65],[3000,8000]]
motif2 = [[60,60,64],[3224,10000]] #3062
motif4 = [[59,55,59],[2062,10500]]
motif3 = [[60,63,65],[2124,9000]]
motif5 = [[60,63,65],[4000,8000]] #Chromatic
motif6 = [[60,63,65],[4000,8000]] #Augmented
motif7 = [[60,63,65],[2250,3500]] #Bass1
motif8 = [[60,63,65],[6500,8000]] #bass2
motif9 = [[60,63,65],[2250,8000]] #Arab

global motifList
motifList =[motif1,motif2,motif3,motif4,motif5,motif6,motif7,motif8,motif9]

global dispatcher
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/filter", bafana)
dispatcher.map("/filter2", test)
dispatcher.map("/swap",follow)
# dispatcher.map("/section3",section3)

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

print("testttttt")
# lastsection.queue.clear()
## PArt 1.1
#start by listening to first motif
client.send_message("/listen", 1)
print("sent")
current = int(motifq.get())
ttime = timeq.get()
currentmotif = motifList[current]
[speed,delayToEnd] = delayT(ttime,currentmotif)
speed = float(speed)
timetoRepeat =random.randint(2, 3)
#we found the motif so wait to play it
time.sleep(float((delayToEnd/1000)-ShimonDelay)) #THE SUBTRACTION IS SHIMONS OFFSET
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
client.send_message("/dance", 0)
time.sleep(5)
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
time.sleep((delayToEnd/1000)-ShimonDelay) # THE SUBTRACTION IS SHIMONS OFFSET
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
    randomizer = random.randint(0,5)
    if randomizer == 5:
        whattodo = 1
    else:
        whattodo = randomizer % 2

    currentmotif = newTempMotif[whattodo]
    if whattodo < 2:
        print("play!",whattodo)
        client.send_message("/play", [whattodo,speed])
        
    else:
        whattodo = 1
        print("waiting")
        client.send_message("/breath", 1)
    delayToEnd = float(newTempMotif[whattodo][1][1]/1000)
    client.send_message("/breath", 0)
    time.sleep(delayToEnd)

print("uh oh")


lastsection.get()
print("what now")

currentmot = lastsection.get()
# input("wait?????")
delayToEnd = newTempMotif[currentmot][1][1]
# time.sleep(delayToEnd)

client.send_message("/listen2", 2)
# input("next")
print("sent")
# lastsection.queue.clear()


####### This is the section where shimon groups the motifs and sill play the group you played in #######

# motifswap = int(2)
# while lastsection.empty() == True:
#     # print("ar2?")
#     if motifswapper.empty() == False:
#         print("swapper?")
        
    
#         motifswap = motifswapper.get()
#         print(motifswap)
#     randomizer = random.randint(0,6)
#     if randomizer == 6:
#         whattodo = 1
#         silence =2
#     else:
#         whattodo = randomizer % 2
#         silence = 1

#     currentmotif = newTempMotif[motifswap + whattodo]
#     if silence < 2:
#         print("play!",whattodo)
#         client.send_message("/play", [motifswap + whattodo,speedF])
        
#     else:
#         whattodo = 1
#         print("waiting")
#     delayToEnd = float(newTempMotif[motifswap+whattodo][1][1]/1000)
#     time.sleep(delayToEnd)
# print("ar3?")
# lastsection.get()
# print("wait for end")
# lastsection.get()
# print("end")




###### This is the section where Shimon plays the last 2 motifs you have played ######
client.send_message("/listen2", 3)
# lastsection.queue.clear()
count = 0
print('her??')



print("clear q")
if lastsection.empty() == False:
    x = lastsection.get()
    print(count,x)
    count += 1
if motifswapper.empty() == False:
    x = motifswapper.get()
    print(count,x)
    count += 1
print('doujbleclear')
motifswap = [2,1]
while lastsection.empty() == True:
    if motifswapper.empty() == False:
        motifswap = motifswapper.get()
        print(motifswap)
    randomizer = random.randint(0,8)
    if randomizer == 6:
        whattodo = 2
        motifplay = motifswap[0]
    else:
        whattodo = randomizer % 2
        motifplay = motifswap[whattodo]
        motifs = int(motifplay)
    currentmotif = newTempMotif[motifplay]
    
    if whattodo < 2:
        print("play!",whattodo)
        client.send_message("/play", [motifs,speed])
        
    else:
        whattodo = 1
        print("waiting")
        client.send_message("/breath", 1)
    delayToEnd = float(newTempMotif[whattodo][1][1]/1000)
    client.send_message("/breath", 0)
    time.sleep(delayToEnd)

lastsection.get()
print("wait for end")

# lastsection.get()
print("double motifs")
client.send_message("/endsong", 1)
client.send_message("/listen2", 4)

client.send_message("/doubleplay",1)
lastsection.get()


# client.send_message("/doubleplay")
# client.send_message("/listen", 4)
print("end")

lastsection.get()
for i in range(1):
    client.send_message("/play", [0,speed])
    delayToEnd = float(newTempMotif[0][1][1]/1000)
    time.sleep(delayToEnd)
#ending
#play the two sections one on either hand (bass two on bottom, raga penta arab on top
# When gil plays the original motif, shimon plays the original motif
# Shimon plays original 3 times

















# See PyCharm help at https://www.jetbrains.com/help/pycharm/