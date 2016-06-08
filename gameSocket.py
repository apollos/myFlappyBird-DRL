import os
import socket
import threading
import time
import Queue
import struct, pickle

mySock = 0
srcSock = 0
ctlSock = 0
'''
threads = []
ctrlStat = 0
mutexs = []
gameDataQ = None
'''
lastScore = 0
olddataLen = 0
rcvCount =0

def startServer():
    global mySock
    global srcSock
    global ctlSock
    '''
    global threads
    global mutexs
    global gameDataQ
    '''
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
    '''  
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
    t3.setDaemon(True)
    t3.start()
    '''
    return 0

def closeServer():
    global mySock
    global srcSock
    global ctlSock  
    '''
    global threads
    global ctrlStat
    global mutexs
    global gameDataQ
    '''
    srcSock.close()  
    mySock.close()  
    ctlSock.close()  
    '''
    threads = []
    ctrlStat = 0
    mutexs = []
    if(gameDataQ):
        gameDataQ.clear()
        gameDataQ = None
    '''
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
        bytes = sndSock.send(data.ljust(int(datalen)))
    except Exception as ex:  
            print "Destination connection broken"
    except KeyboardInterrupt:  
            print "Interrupted!"  
    return bytes
'''
def ctrlThread():
    
    global ctlSock
    global ctrlStat
    global mutexs
    mutex = mutexs[0]
    if ctlSock == 0:
        print "CTRL Socket Error!"
        return 1
    while True: 
        stringData = rcvDataFromSocket(ctlSock, 16)
        
        if len(stringData) == 0:#recv error
            if mutex.acquire(1):
                ctrlStat = 2
                mutex.release()
            break
        data = int(stringData.strip("\x00").strip(" "))
        
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
    mutex = mutexs[1]
    if srcSock == 0:
        print "CTRL Socket Error!"
        return 1
    while True: 
        stringData = rcvDataFromSocket(srcSock, 16)
        if len(stringData) == 0:#recv error
            if mutex.acquire(1):
                ctrlStat = 2
                mutex.release()
            break
        dataLen = int(stringData)
        stringData = rcvDataFromSocket(srcSock, dataLen)
        if len(stringData) == 0:#recv error
            if mutex.acquire(1):
                ctrlStat = 2
                mutex.release()
            break
        unpackStr = '!i?%ds' % (dataLen - 5)
        score, terminal, image_data = struct.unpack(unpackStr, stringData)
        image_data = pickle.loads(image_data)
        #print "RCV Len %d" % dataLen
        #if mutex.acquire(1):
        gameDataQ.put((score, terminal, image_data))
        #    mutex.release()

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
'''

def frame_step(input_actions):
    '''
    global mutexs
    global gameDataQ
    '''    
    global olddataLen, rcvCount

    #Send action to remote and get score, crash, image from remote
    #print str(input_actions)
    if (sndDataFromSocket(srcSock, str(input_actions), 16) == 0):
        print "Snd Error!"
        return None, None, None, True    
    # check for score, comparing with last, if >1, reward = newScore - oldScore
    #mutex = mutexs[1]
    #multiple thread may cause the trainig async, I need consider the potential issue later
    # check if crash here, if crash, terminal = True and reward = -1
    #if mutex.acquire(1):
    '''
    try:
        print gameDataQ.qsize()
        (score, crash, image_data) = gameDataQ.get(True, 0.5)
    except Queue.Empty:
        #generally, shall be game over now
        return None, None, None, False
    '''    
    ##################################################################
    stringData = rcvDataFromSocket(srcSock, 16)
    if len(stringData) == 0:#recv error
        print "Rcv Error!"
        return None, None, None, True
    dataLen = int(stringData)
    if olddataLen != dataLen:        
        print "Old Len %d, new Len %d" % (olddataLen, dataLen)
        olddataLen = dataLen
    stringData = rcvDataFromSocket(srcSock, dataLen)
    if len(stringData) == 0:#recv error
        print "Rcv Error!"
        return None, None, None, True
    unpackStr = '!f?%ds' % (dataLen - 5)
    reward, terminal, image_data = struct.unpack(unpackStr, stringData)
    image_data = pickle.loads(image_data) 
    rcvCount += 1
    #print "Rcv %d" %(rcvCount)   

    ##################################################################
    #    mutex.release()    
    #print "c t d", "[",crash,"]", "[",terminal,"]", "[",image_data,"]", 
    return image_data, reward, terminal, False

def clearGlobalPara():
    global lastScore
    lastScore = 0
        
