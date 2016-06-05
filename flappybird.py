# -------------------------
# Project: Deep Q-Learning on Flappy Bird
# Author: Yu Song
# Date: 2016.6.4
# -------------------------

import cv2
import flappyBirdWrap
from brainDQN import BrainDQN
import numpy as np


testImage = 0

# preprocess raw image to 80*80 gray image, will change back to rgb later
def preprocess(observation):
    global testImage
    if(testImage == 0):
        testImage = 1
        cv2.imwrite("./first.png", observation)
	observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
	ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
	return np.reshape(observation,(80,80,1))

def playFlappyBird():
    #init BrainDQN
    actions = 2
    
    brain = BrainDQN(actions)
    #play the game forever
    
    while True: 
        #init Flappy Bird Game
        flappyBirdWrap.startServer()
        while True:
            if(flappyBirdWrap.getSignal() == 1): #Start Game
                action0 = np.array([0,1])
                observation0, reward0, terminal = flappyBirdWrap.frame_step(action0) #send a key action to the flappy game to start
	    #Ready for playing game
	    #obtain init state
	    action0 = np.array([1,0])  # do nothing, [0]=1 do nothing, [1]=1 "space key or up key"
	    observation0, reward0, terminal = flappyBirdWrap.frame_step(action0)
	    observation0 = cv2.cvtColor(cv2.resize(observation0, (80, 80)), cv2.COLOR_BGR2GRAY)
	    ret, observation0 = cv2.threshold(observation0,1,255,cv2.THRESH_BINARY)
	    brain.setInitState(observation0)

	    #run the game
	    while True:
		    action = brain.getAction()
		    nextObservation,reward,terminal = flappyBirdWrap.frame_step(action)
            if(not reward): #something wrong
                print "flappyBirdWrap.frame_step Error!"
                break
            nextObservation = preprocess(nextObservation)
            brain.setPerception(nextObservation,action,reward,terminal)
            if(flappyBirdWrap.getSignal() == 2):
                print "Stop game!"
                break
        #clean everything and wait again
        flappyBirdWrap.closeServer()


def main():
	playFlappyBird()

if __name__ == '__main__':
	main()
