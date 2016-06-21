# -------------------------
# Project: Deep Q-Learning on Flappy Bird
# Author: Yu Song
# Date: 2016.6.4
# -------------------------

import gameSocket
from brainDQN import BrainDQN
import numpy as np
import sys
import cv2

testImage = 0

# preprocess raw image to 80*80 gray image, will change back to rgb later

def preprocess(observation):
    '''
    global testImage    
    if(testImage >= 0):
        testImage += 1
        picName = "./pic%04d.jpeg" % testImage
        print picName
        cv2.imwrite(picName, observation)
    '''
    return np.reshape(observation,(80,80,1))

def playFlappyBird():
    #init BrainDQN
    actions = 2
    brain = BrainDQN(actions)
    #play the game forever
    
    gameSocket.startServer()
    while True: 
        #init Flappy Bird Game
        gameSocket.clearGlobalPara()
        '''
        while True:     
            rst = flappyBirdWrap.getSignal()       
            if( rst == 1): #Start Game
                action0 = np.array([0,1])
                observation0, reward0, terminal, quitFlag = flappyBirdWrap.frame_step(action0) #send a key action to the flappy game to start    
                if quitFlag:
                    return
                break
            elif( rst == 2): #stop Game
                break
            time.sleep(1)
        if rst == 2:
            flappyBirdWrap.closeServer()
            time.sleep(1)
            continue
        '''
        '''
        action0 = np.array([0,1]) #Start Game
        observation0, reward0, terminal, quitFlag = flappyBirdWrap.frame_step(action0)
        '''
        #Ready for playing game
        #obtain init state    
        # do nothing, [0]=1 do nothing, [1]=1 "space key or up key"    
        action = [1, 0]
        observation, reward, terminal, quitFlag = gameSocket.frame_step(action[1])
       
        if quitFlag:
            return
        if observation is None:
            #something wrong
            print "observation is None"
            continue
        
        brain.setInitState(observation)

        #run the game
        while True:
            action = map(int, brain.getAction())
            nextObservation,reward,terminal, quitFlag = gameSocket.frame_step(action[1])          

            if quitFlag:
                return
            if(reward is None): #something wrong
                #print "flappyBirdWrap.frame_step Error!"
                break

            nextObservation = preprocess(nextObservation)
            brain.setPerception(nextObservation,action,reward,terminal)
            
            if(gameSocket.getSignal() == 2):
                print "Stop game!"
                break  
             
            if(terminal):
                break    
    #clean everything and wait again
    gameSocket.closeServer()
        


def main():
    playFlappyBird()

if __name__ == '__main__':
    main()
