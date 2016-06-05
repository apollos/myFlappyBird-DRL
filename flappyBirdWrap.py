import os
import socket
import threading
import time
import Queue
import struct, pickle

mySock = 0
srcSock = 0
ctlSock = 0
threads = []
ctrlStat = 0
mutexs = []
gameDataQ = None
lastScore = 0

def startServer():
    global mySock
    global srcSock
    global ctlSock
    global gameData
    global threads
    global mutexs
    global gameDataQ
    global lastScore

    mySock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
    SOCKNUM = 2
    HOST = "0.0.0.0"
    PORT = 9129
    mySock.bind((HOST, PORT))  
    mySock.listen(SOCKNUM)  
    print "Start Server!"
    srcSock, src_addr = mySock.accept()  
    print "Source Channel Connected by", src_addr  
      
    ctlSock, dst_addr = mySock.accept()  
    print "Control Channel Connected by", dst_addr

    lastScore = 0
    gameDataQ = Queue.Queue(maxsize = 128) #FIFO 
    t1 = threading.Thread(target=ctrlThread)
    threads.append(t1)
    mutex1 = threading.Lock()
    mutexs.append(mutex1)
    t1.setDaemon(True)
    t1.start()

    t2 = threading.Thread(target=gameDataThread)
    threads.append(t2)
    mutex2 = threading.Lock()
    mutexs.append(mutex2)
    t2.setDaemon(True)
    t2.start()

    t3 = threading.Thread(target=showInforThread)
    threads.append(t3)    
    t2.setDaemon(True)
    t2.start()
    return 0

def closeServer():
    global mySock
    global srcSock
    global ctlSock  
    global threads
    global ctrlStat
    global mutexs
    global gameDataQ

    srcSock.close()  
    mySock.close()  
    ctlSock.close()  
    
    threads = []
    ctrlStat = 0
    mutexs = []
    if(gameDataQ):
        gameDataQ.clear()
        gameDataQ = None
    return 0


def rcvDataFromSocket(rcvSock, dataLen):
    DataValue = ''
    while len(DataValue) < dataLen:
        try:
            packet = rcvSock.recv(dataLen - len(DataValue))
        except Exception as ex:  
            print "recvall error Exception!"
            DataValue = ''
            break
        if packet == None or len(packet) == 0:
            print "recvall error, zero packet"
            DataValue = ''
            break
        DataValue += packet
    return DataValue

def sndDataFromSocket(sndSock, data, datalen):
    bytes = 0
    try:  
        bytes = sndSock.send(str(data).ljust(int(datalen)))
    except Exception as ex:  
            print "Destination connection broken"
    except KeyboardInterrupt:  
            print "Interrupted!"  
    return bytes

def ctrlThread():
    
    global ctlSock
    global ctrlStat
    global mutexs

    if ctlSock == 0:
        print "CTRL Socket Error!"
        return 1
    while True: 
        stringData = rcvDataFromSocket(ctlSock, 16)

        if len(stringData) == 0:#recv error
            break
        data = int(stringData.strip("\x00").strip(" "))

        mutex = mutexs[0]
        if(data == 1):  #Start
            if mutex.acquire(1):
                ctrlStat = data
                mutex.release()
        elif(data == 2): #Stop
            if mutex.acquire(1):
                ctrlStat = data
                mutex.release()
                break
        else:
            print "CTRL Socket RCV unknowed command %d" % data

def gameDataThread():
    global srcSock
    global mutexs
    global gameDataQ

    if srcSock == 0:
        print "CTRL Socket Error!"
        return 1
    while True: 
        stringData = rcvDataFromSocket(srcSock, 16)
        if len(stringData) == 0:#recv error
            break
        dataLen = int(stringData)
        stringData = rcvDataFromSocket(srcSock, dataLen)
        unpackStr = '!i?%ds' % (dataLen - 5)
        score, terminal, image_data = struct.unpack(unpackStr, stringData)
        image_data = pickle.loads(image_data)
        mutex = mutexs[1]
        if mutex.acquire(1):
            gameDataQ.put((score, terminal, image_data))
            mutex.release()

def showInforThread():
    while True:
        if gameDataQ:
            if (gameDataQ.qsize() != 0):
                print gameDataQ.qsize()
        time.sleep(10) #10 seconds

def getSignal():
    global ctrlStat
    global mutexs
    mutex = mutexs[0]
    data = 0 #unknown
    if mutex.acquire(0):
        data = ctrlStat 
        mutex.release()
    return data

def frame_step(input_actions):

    global mutexs
    global gameDataQ
    global lastScore
    reward = 0.1
    terminal = False

    if sum(input_actions) != 1:
        print ('Multiple input actions!')
        return None, None, None

    if input_actions[1] == 1:
        #Send action to remote and get score, crash, image from remote
        if (sndDataFromSocket(srcSock, input_actions, 16) == 0):
            return None, None, None

        # check for score, comparing with last, if >1, reward = newScore - oldScore
        mutex = mutexs[1]
        #multiple thread may cause the trainig async, I need consider the potential issue later
        # check if crash here, if crash, terminal = True and reward = -1
        if mutex.acquire(1):
            (score, crash, image_data) = gameDataQ.get()
            mutex.release()
        if (crash):
            reward = -1
            terminal = True
        elif (score > lastScore):
            lastScore = score
            reward = 1
        elif (score == lastScore):
            reward = 0.1
        else:#strange issue, I do not knwo why
            print"Last score is %d, now is %d" % (lastScore, score)
            return None, None, None       

        return image_data, reward, terminal


        
