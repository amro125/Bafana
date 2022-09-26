
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



# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def test(name,*args):
    totalt = np.sum(np.array(list(args)))
    timeq.put(totalt)

def motifRecognizer(name,*args):
    receivedm = np.sum(np.array(list(args)))
    if not desiredm.empty():
        testm = desiredm.get()
    else:
        testm = [-1, -1] # something that will never be true
    motifnum = int(receivedm)
    for m in testm:
        if m == motifnum:
            motifq.put(motifnum)

def follow(name,*args):
    received = np.array(list(args))
    motifswapper.put(received)

def delayT(tElapse,motif):
    sectiont = motif[1][0]
    totalT = motif[1][1]
    ratio = tElapse/sectiont
    delayToEnd =  (ratio*totalT) - tElapse
    speed = 1024/ratio #1024 is 1X speed
    return [speed,delayToEnd]


def section1():
    current = int(motifq.get)
    tempo1 = timeq.get()
    currentmotif = motifList[current]
    [speed, delayToEnd] = delayT(tempo1, currentmotif)
    speed = float(speed)
    timetoRepeat = random.randint(2, 3)
    # we found the motif so wait to play it
    time.sleep(float((delayToEnd / 1000) - ShimonDelay))  # THE SUBTRACTION IS SHIMONS OFFSET
    print(current, speed)
    client.send_message("/play", [current, speed])

    delaytoEndpt1 = float((tempo1 / currentmotif[1][0]) * (currentmotif[1][1]) / 1000)
    print(delaytoEndpt1)
    time.sleep(delaytoEndpt1)
    i = 0
    # play it a couple times
    for i in range(timetoRepeat):
        client.send_message("/play", [current, speed])
        print("again", delaytoEndpt1)
        time.sleep(delaytoEndpt1)
        print("again2")
    # print("done")
    # We wait a little bit to let Gil play the motif, then we repeat it
    client.send_message("/dance", 0)
    time.sleep(5)
    print("next part")
    client.send_message("/play", [current, speed])
    time.sleep(delaytoEndpt1)

def section2():
    current = int(motifq.get())
    ttime = float(timeq.get())
    currentmotif = motifList[current]
    [speed, delayToEnd] = delayT(ttime, currentmotif)
    speedF = float(speed)
    # this speed is the the final speed for the rest of the piece
    # Lets calculate the correct times to wait for each motif
    ratio = ttime / currentmotif[1][0]
    global newTempMotif
    newTempMotif = motifList
    i = 0
    for motif in motifList:
        newTempMotif[i][1][1] = float(ratio * motif[1][1])
        newTempMotif[i][1][0] = float(ratio * motif[1][0])
        i += 1
    newTempMotif = motifList
    i = 0
    for motif in motifList:
        newTempMotif[i][1][1] = float((ratio * motif[1][1])/1000)
        newTempMotif[i][1][0] = float((ratio * motif[1][0])/1000)
        i += 1

    # Now we can use this as a delaytoend

    timetoRepeat = random.randint(2, 3)
    # we found the motif so wait to play it
    time.sleep((delayToEnd) - ShimonDelay)  # THE SUBTRACTION IS SHIMONS OFFSET
    client.send_message("/play", [current, speedF])
    delaytoEnd2 = float((ttime / currentmotif[1][0]) * (currentmotif[1][1]))
    i = 0
    # play it a couple times
    for i in range(timetoRepeat):
        client.send_message("/play", [current, speedF])
        time.sleep(delaytoEnd2)
    #### Alternate between motif 1 and 2 ###
    client.send_message("/listen2", 1)
    desiredm.put([2, 3])
    print("damn we made it")
    while motifq.empty() == True:
        randomizer = random.randint(0, 5)
        if randomizer == 5:
            whattodo = 1
        else:
            whattodo = randomizer % 2

        currentmotif = newTempMotif[whattodo]
        if whattodo < 2:
            print("play!", whattodo)
            client.send_message("/play", [whattodo, speedF])

        else:
            whattodo = 1
            print("waiting")
            client.send_message("/breath", 1)
        delayToEnd = float(newTempMotif[whattodo][1][1])
        client.send_message("/breath", 0)
        t_start = time.time()
        t_count = 0
        while t_count < delayToEnd:
            t_check  = time.time()
            t_count = t_check - t_start
            time.sleep(0.001)
            if motifq.empty() == False:
                break
        end = int(motifq.get())
        endt = float((newTempMotif[end][1][1] - newTempMotif[end][1][0]))
        time.sleep(endt - ShimonDelay)
    return speedF, newTempMotif, end


def section3():
    motifswap = [2,3]
    while motifq.empty() == True:
        if motifswapper.empty() == False:
            motifswap = motifswapper.get()
            print(motifswap)
        randomizer = random.randint(0, 8)
        if randomizer == 6:
            whattodo = 2
            motifplay = motifswap[0]
        else:
            whattodo = randomizer % 2
            motifplay = motifswap[whattodo]
            motifs = int(motifplay)

        if whattodo < 2:
            print("play!", whattodo)
            client.send_message("/play", [motifs, speedFin])

        else:
            whattodo = 1
            print("waiting")
            client.send_message("/breath", 1)
        delayToEnd = float(newTempMotif[whattodo][1][1])
        t_start = time.time()
        t_count = 0
        while t_count < delayToEnd:
            t_check  = time.time()
            t_count = t_check - t_start
            time.sleep(0.001)
            if motifq.empty() == False:
                break
    end = int(motifq.get())
    endt = float((newTempMotif[end][1][1] - newTempMotif[end][1][0]))
    time.sleep(endt - ShimonDelay)
    return end


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    global IP
    global PORT_FROM_MAX
    global PORT_TO_MAX
    global ShimonDelay
    global motifList
    IP = "127.0.0.1"
    PORT_FROM_MAX = 5007
    PORT_TO_MAX = 5010
    ShimonDelay = 0.50

    # OSC Listening
    # global timeq
    # global pieceq
    # global listen
    # global lastsection
    timeq = queue.Queue()
    motifq = queue.Queue()
    # liten = queue.Queue()
    # lastsection = queue.Queue()
    motifswapper = queue.Queue()
    desiredm = queue.Queue()
    # midi BPM is 120
    motif1 = [[60, 64, 65], [3000, 8000]]
    motif2 = [[60, 60, 64], [3224, 10000]]  # 3062
    motif4 = [[59, 55, 59], [2062, 10500]]
    motif3 = [[60, 63, 65], [2124, 9000]]
    motif5 = [[60, 63, 65], [4000, 8000]]  # Chromatic
    motif6 = [[60, 63, 65], [4000, 8000]]  # Augmented
    motif7 = [[60, 63, 65], [2250, 3500]]  # Bass1
    motif8 = [[60, 63, 65], [6500, 8000]]  # bass2
    motif9 = [[60, 63, 65], [2250, 8000]]  # Arab

    motifList = [motif1, motif2, motif3, motif4, motif5, motif6, motif7, motif8, motif9]

    global dispatcher
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/motif", motifRecognizer)
    dispatcher.map("/time", test)
    dispatcher.map("/follow", follow)


    def server():
        server = osc_server.ThreadingOSCUDPServer((IP, PORT_FROM_MAX), dispatcher)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()
        atexit.register(server.server_close())


    threading.Thread(target=server, daemon=True).start()
    global client
    client = udp_client.SimpleUDPClient(IP, PORT_TO_MAX)

    section = 1

    ##### Section 1 #######
    client.send_message("/listen", 1)
    desiredm.put([0, 1])
    section1()

    ##### Section 2 #######
    global speedFin
    global newMotifList
    desiredm.put([0, 1])
    speedFin, newMotifList,lastMotif  = section2()
    # UNCOMMENT BELOW TO SET TEMPO MANUALLY
    # speedFin = 1024
    # newMotifList = 2
    print(speedFin)

    randomplay = random.randint(2, 3)
    client.send_message("/inter", 1)
    for i in range(randomplay):
        client.send_message("/play", [lastMotif, speedFin])
        time.sleep(newMotifList[lastMotif][1][1])

    #### Section 3 ########
    client.send_message("/listen2", 3)
    desiredm.put([6])
    bassmotif = section3()
    client.send_message("/inter", 1)
    for i in range(3):
        client.send_message("/play", [bassmotif, speedFin])
        time.sleep(newMotifList[bassmotif][1][1])

    #### Section 4 #######
    # we run this section in MAx so just send a start command
    client.send_message("/inter", 1)
    client.send_message("/doubleplay", 1)

    #### Section 5 #######
    desiredm.put([0]) #listening only for original motif
    finalmotif = motifq.get()
    delay = float((newTempMotif[finalmotif][1][1] - newTempMotif[finalmotif][1][0]) - ShimonDelay)
    time.sleep(delay)
    client.send_message("/finale", 1)
    for i in range(3):
        client.send_message("/play", [finalmotif, speedFin])
        delayToEnd = float(newTempMotif[finalmotif][1][1])
        time.sleep(delayToEnd)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
