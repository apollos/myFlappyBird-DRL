import os
import socket
import threading
import time
import Queue
import struct, pickle
import cv2, numpy
import cv2.cv as cv

mySock = 0
srcSock = 0
#ctlSock = 0

threads = []
ctrlStat = 0
mutexLock = None

gameDataQRcv = None
gameDataQSnd = None

lastScore = 0
olddataLen = 0
rcvCount =0 

def startServer(sndOnly):
    global mySock
    global srcSock
    #global ctlSock
    
    global threads
    global mutexLock
    global gameDataQRcv, gameDataQSnd
    
    global lastScore, imgSnd

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
    '''
    lastScore = 0
    gameDataQRcv = Queue.Queue(maxsize = 128) #FIFO 
    gameDataQSnd = Queue.Queue(maxsize = 128)
    '''
    t1 = threading.Thread(target=ctrlThread)
    threads.append(t1)
    mutex1 = threading.Lock()
    mutexs.append(mutex1)
    t1.setDaemon(True)
    t1.start()
    '''
    mutexLock = threading.Lock()
    if not sndOnly:        
        t2 = threading.Thread(target=gameDataRcvThread)
        threads.append(t2)
        t2.setDaemon(True)
        t2.start()
        
        t21 = threading.Thread(target=gameDataSndThread)
        threads.append(t21)
        t21.setDaemon(True)
        t21.start()
    else:
        imgSnd = cv.CreateImageHeader((288, 512), cv.IPL_DEPTH_8U, 3)  
        t21 = threading.Thread(target=gameFrameSndThread)
        threads.append(t21)
        t21.setDaemon(True)
        t21.start()        

    t3 = threading.Thread(target=showInforThread)
    threads.append(t3)    
    t3.setDaemon(True)
    t3.start()
    
    return 0

def closeServer():
    global mySock
    global srcSock
    #global ctlSock  
    
    global threads
    global ctrlStat
    global mutexLock
    global gameDataQRcv, gameDataQSnd
    
    srcSock.close()  
    mySock.close()  
    #ctlSock.close()  
    
    threads = []
    ctrlStat = 0
    mutexLock = None
    if(gameDataQRcv):
        gameDataQRcv.clear()
        gameDataQRcv = None
    if(gameDataQSnd):
        gameDataQSnd.clear()
        gameDataQSnd = None
    
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
    sndbytes = 0
    try:  
        sndbytes = sndSock.send(data.ljust(int(datalen)))
    except Exception as ex:  
            print "Destination connection broken"
    except KeyboardInterrupt:  
            print "Interrupted!"  
    return sndbytes
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
'''
def gameDataRcvThread():
    global srcSock
    global gameDataQRcv
    global ctrlStat
    global mutexLock
    
    if srcSock == 0:
        print "Data Socket Error!"
        return 1
    while True: 
        stringData = rcvDataFromSocket(srcSock, 16)
        if len(stringData) == 0:#recv error
            if mutexLock.acquire(1):
                ctrlStat = 2
                mutexLock.release()
            break
        dataLen = int(stringData)
        stringData = rcvDataFromSocket(srcSock, dataLen)
        if len(stringData) == 0:#recv error
            if mutexLock.acquire(1):
                ctrlStat = 2
                mutexLock.release()
            break
        unpackStr = '!f?%ds' % (dataLen - 5)
        reward, terminal, image_data = struct.unpack(unpackStr, stringData)
        image_data = pickle.loads(image_data)          
        #print "RCV Len %d" % dataLen
        gameDataQRcv.put((reward, terminal, image_data))

def gameDataSndThread():
    global srcSock
    global gameDataQSnd
    global ctrlStat
    global mutexLock

    if srcSock == 0:
        print "Data Socket Error!"
        return 1
    while True: 
        input_actions = gameDataQSnd.get(True, 5)        
        if (sndDataFromSocket(srcSock, str(input_actions), 16) == 0):
            print "Snd Error!"
            if mutexLock.acquire(1):
                ctrlStat = 2
                mutexLock.release()
                break
testImage = 0
def gameFrameSndThread():
    global srcSock
    global gameDataQSnd
    global ctrlStat
    global mutexLock

    if srcSock == 0:
        print "Data Socket Error!"
        return 1
    #imgSnd = cv.CreateImageHeader((288, 512), cv.IPL_DEPTH_8U, 3) 
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),75]
    while True: 
        img = gameDataQSnd.get(True, 5) 
        #opencvImage = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
        buff = numpy.fromstring(img,numpy.uint8)
        buff = buff.reshape(512,288,3)
        result, imgencode = cv2.imencode('.jpg', buff, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()        
 
        try:  
            dataLen = len(stringData)
            bytes = sndDataFromSocket(srcSock, str(dataLen), 16);
            bytes += sndDataFromSocket(srcSock, stringData, dataLen);            
            if bytes == 0:
                if mutexLock.acquire(1):
                    ctrlStat = 2
                    mutexLock.release()            
                break
        except KeyboardInterrupt:  
            print "Interrupted!" 
            if mutexLock.acquire(1):
                ctrlStat = 2
                mutexLock.release() 
            break

def showInforThread():
    while True:
        if gameDataQRcv:
            if (gameDataQRcv.qsize() != 0):
                print gameDataQRcv.qsize()
        time.sleep(10) #10 seconds

def getSignal():
    global ctrlStat
    global mutexLock

    data = 0 #unknown
    if mutexLock.acquire(0):
        data = ctrlStat 
        mutexLock.release()
    return data


def frame_step(input_actions):
    
    global gameDataQRcv, gameDataQSnd
    global olddataLen, rcvCount

    #Send action to remote and get score, crash, image from remote
    #print str(input_actions)
    gameDataQSnd.put(input_actions)    

    #multiple thread may cause the trainig async, I need consider the potential issue later
    try:
        #print gameDataQRcv.qsize()
        (reward, terminal, image_data) = gameDataQRcv.get(True, 5)
    except Queue.Empty:
        #generally, shall be game over now
        return None, None, None, False        
    
    #    mutex.release()    
    #print "c t d", "[",reward,"]", "[",terminal,"]", "[",image_data,"]", 
    return image_data, reward, terminal, False

def frame_snd(imageData):
    gameDataQSnd.put(imageData)    

def clearGlobalPara():
    global lastScore
    lastScore = 0
        
