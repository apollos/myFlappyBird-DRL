# -------------------------
# Project: Deep Q-Learning on Flappy Bird
# Author: Yu Song
# Date: 2016.6.4
# -------------------------

import cv2
import cv2.cv as cv
import sys
sys.path.append("game/")
import wrapped_flappy_bird as game

from brainDQN import BrainDQN
import numpy as np
import time
import gameSocket


testImage = 0

# preprocess raw image to 80*80 gray image, will change back to rgb later

def preprocess(observation, screenCap):
    observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
    ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
    return np.reshape(observation,(80,80,1))

def playFlappyBird():
    #init BrainDQN
    actions = 2
    brain = BrainDQN(actions)
    quitFlag = False
    #play the game forever
    
    flappyBird = game.GameState()
    gameSocket.startServer(True)
    cv.NamedWindow("pil2ipl")

    while True: 
        #init Flappy Bird Game    
        gameSocket.clearGlobalPara()        
        action = np.array([1,0])        
        observation, reward, terminal, screenCap = flappyBird.frame_step(action)
        gameSocket.frame_snd(screenCap)
        if(gameSocket.getSignal() == 2):
            print "Stop game!"
            quitFlag = True
            break 
           
        observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
        ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)        
        brain.setInitState(observation)

        #run the game
        while True:            
            action = brain.getAction()            
            nextObservation,reward,terminal, screenCap = flappyBird.frame_step(action)       
            gameSocket.frame_snd(screenCap)
            nextObservation = preprocess(nextObservation, screenCap)
            brain.setPerception(nextObservation,action,reward,terminal)
            if(gameSocket.getSignal() == 2):
                print "Stop game!"
                quitFlag = True
                break 
        if quitFlag:
            return
    gameSocket.closeServer()

def main():
    playFlappyBird()

if __name__ == '__main__':
    main()
