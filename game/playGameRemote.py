# -------------------------
# Project: Deep Q-Learning on Flappy Bird
# Author: Yu Song
# Date: 2016.6.4
# -------------------------

import cv2
import sys
import wrapped_flappy_bird as game
import socket
import pickle
import struct

robotSock = 0

def sndDataToRobot(sndSock, data, datalen):
    
    sndBytes = 0
    try:  
        sndBytes = sndSock.send(str(data).ljust(int(datalen)))
    except socket.error, e:
            # Something else happened, handle error, exit, etc.
        print e

    return sndBytes

def compressImg(observation):
    
    observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
    ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
    return observation 

sndCount = 0
def saveGameStatus(observation, reward, terminal):
    global robotSock, sndCount
    if(robotSock):
        image_data_pickle = pickle.dumps(observation)
        packStr = '!f?%ds' % len(image_data_pickle)
        sndStr = struct.pack(packStr, reward, terminal, image_data_pickle)
        if(sndDataToRobot(robotSock, len(sndStr), 16) != 16):
            return
        sndDataToRobot(robotSock, sndStr, len(sndStr))
        sndCount +=1
        #print "Snd %d" % (sndCount)

def cleanConnect():
    global robotSock
    robotSock.close()

def connectWithRobot(host, port):
    global robotSock
    robotSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #robotSock.settimeout(0.04)
    robotSock.connect((host, int(port)))  
    print "Host %s connected\n" % (host)

def rcvDataFromRobot(rcvSock, dataLen):
    DataValue = ''
    flag = True
    while len(DataValue) < dataLen:
        try:
            packet = rcvSock.recv(dataLen - len(DataValue))
        except socket.timeout, e:
            err = e.args[0]
            # this next if/else is a bit redundant, but illustrates how the
            # timeout exception is setup
            if err == 'timed out':
                break
            else:
                print e
                flag = False
                break
        except socket.error, e:
            # Something else happened, handle error, exit, etc.
            print e
            flag = False
            break
        else:
            if len(packet) == 0:
                print 'Remote Close!'
                flag = False
                break
            else:
                # got a message do something :)
                DataValue += packet
    return DataValue, flag

def main(argv):
    if len(argv) != 3:
        print ("Usage: python playGameRemote.py [<target ip> <port>]")
        exit(-1)
    host = argv[1]
    port = argv[2]
    connectWithRobot(host, port)
    flappyBird = game.GameState()    
    while True: 
        #Play Flappy Bird Game  
        rcvData, flag = rcvDataFromRobot(robotSock, 16)
        if (not flag):      
            print "rcvDataFromRobot Failed!"
            break
        rcvData = rcvData.strip("\x00").strip(" ")           
        if (len(rcvData) != 0):            
            action = int(rcvData)
            
            if action == 1:
                actions = [0,1]
            else:
                actions = [1,0]
            observation, reward, terminal = flappyBird.frame_step(actions)
            observation = compressImg(observation)
            saveGameStatus(observation, reward, terminal)
        else:
            print "rcvData is 0"
            break
    cleanConnect()

if __name__ == '__main__':
    main(sys.argv)
