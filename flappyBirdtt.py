# -------------------------
# Project: Deep Q-Learning on Flappy Bird
# Author: Yu Song
# Date: 2016.6.4
# -------------------------

from brainDQN import BrainDQN
import numpy as np
import sys
import cv2
sys.path.append("game/")
import wrapped_flappy_bird as game


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
    
    flappyBird = game.GameState()
    while True: 
        #init Flappy Bird Game
        
        #Ready for playing game
        #obtain init state    
        # do nothing, [0]=1 do nothing, [1]=1 "space key or up key"            
        action = np.array([1,0]) 
        observation, reward, terminal = flappyBird.frame_step(action)     
        observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
        ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)           
        brain.setInitState(observation)

        #run the game
        while True:
            action = brain.getAction()
            nextObservation,reward,terminal = flappyBird.frame_step(action) 
            nextObservation = cv2.cvtColor(cv2.resize(nextObservation, (80, 80)), cv2.COLOR_BGR2GRAY)
            ret, nextObservation = cv2.threshold(nextObservation,1,255,cv2.THRESH_BINARY)           
            nextObservation = preprocess(nextObservation)
            brain.setPerception(nextObservation,action,reward,terminal)  
    #clean everything and wait again
     


def main():
    playFlappyBird()

if __name__ == '__main__':
    main()
