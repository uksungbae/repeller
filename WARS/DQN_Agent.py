#encoding: utf-8

##
## DQN_Repeller.py
## ACE 15/08/2018
##

#소리별 랭킹 나타낼 수 있게 reward값 수정 필요
import gym
import random
import ospt
import numpy as np
import time
import datetime
import pygame
import sys, json, select

from collections      import deque
from keras.models     import Sequential
from keras.layers     import Dense
from keras.optimizers import Adam

p = datetime.datetime.now()
rt = datetime.datetime.now() - p

#Initialise pygame and the mixer
pygame.init()
pygame.mixer.init()

#JSON format checker
def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError:
    return False
  return json_object

#Json object checker for detected
def is_detected(obj):
    try:
        detected_obj = obj['detected']
        sys.stdout.flush()
    except KeyError:
        return False
    return detected_obj

#Json object checker for "welldone"
def is_welldone(obj):
    try:
        welldone_obj = obj['welldone']
        sys.stdout.flush()
    except KeyError:
        pass
    return True

# Read a line. Using select for non blocking reading of sys.stdin
def getLine():
    i,o,e = select.select([sys.stdin],[],[],0.0001)
    for s in i:
        if s == sys.stdin:
            input = sys.stdin.readline()
            return input
    return False

def sound_a():
    #load the sound file
    sound = pygame.mixer.Sound("wav/0001.wav")

    #play the sound file for 5 seconds and then stop it
    sound.play()
    time.sleep(5)
    sound.stop()

def sound_b():
    #load the sound file
    sound = pygame.mixer.Sound("wav/0002.wav")

    #play the sound file for 5 seconds and then stop it
    sound.play()
    time.sleep(5)
    sound.stop()
        
def sound_c():
    #load the sound file
    sound = pygame.mixer.Sound("wav/0003.wav")
     
    #play the sound file for 5 seconds and then stop it
    sound.play()
    time.sleep(5)
    sound.stop()
        
def sound_d():
    #load the sound file
    sound = pygame.mixer.Sound("wav/0004.wav")
      
    #play the sound file for 5 seconds and then stop it
    sound.play()
    time.sleep(5)
    sound.stop()


class Agent():
    def __init__(self, state_size, action_size):
        self.weight_backup      = "/home/pi/Projects/WARS/wars_weight.h5"
        self.state_size         = state_size
        self.action_size        = action_size
        self.memory             = deque(maxlen=2000)
        self.learning_rate      = 0.001
        self.gamma              = 0.95
        self.exploration_rate   = 1.0
        self.exploration_min    = 0.01
        self.exploration_decay  = 0.995
        self.brain              = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

        if os.path.isfile(self.weight_backup):
            model.load_weights(self.weight_backup)
            self.exploration_rate = self.exploration_min
        return model

    def save_model(self):
            self.brain.save(self.weight_backup)

    def act(self, state):
        if np.random.rand() <= self.exploration_rate:
            return random.randrange(self.action_size)
        act_values = self.brain.predict(state)
        return np.argmax(act_values[0])

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, sample_batch_size):
        if len(self.memory) < sample_batch_size:
            return
        sample_batch = random.sample(self.memory, sample_batch_size)
        for state, action, reward, next_state, done in sample_batch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.brain.predict(next_state)[0])
            target_f = self.brain.predict(state)
            target_f[0][action] = target
            self.brain.fit(state, target_f, epochs=1, verbose=0)
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay

class Repeller:
    def __init__(self):
        self.sample_batch_size = 32
        self.episodes          = 10000

        self.sounds = np.array([[rt,rt,rt,rt]])
        self.state_size        = self.sounds.shape[1]
        self.action_size       = 4
        self.agent             = Agent(self.state_size, self.action_size)
        self.iamdone           = False
        self.welldone          = False

    def getResult(self, action, returnTimeAction):
        
        if returnTimeAction > self.sounds[0,action]:
            #return a positive reward.
            self.sounds[0,action] = returnTimeAction
            return self.sounds[0], 1, False, {}
        else:
            #return a negative reward.
            self.sounds[0,action] = returnTimeAction
            return self.sounds[0], -1, True, {}

    def run(self):
        try:
            time.sleep(1)
            checkDetected = False
            numOfdetec = 0
            
            while True:               
                state = self.sounds[0]
                #print(state)
                state = np.reshape(state, [1, self.state_size])
                #print(state)
                done = False
                index = 0
                while not done:
                    input = getLine();
                    if(input != False):
                        json_object = is_json(input)
                        if(json_object != False):
                            self.welldone = is_welldone(json_object)
                            checkDetected = is_detected(json_object)
                    else:
                        pass
                    
                    if checkDetected:      #When output from motion sensor is HIGH
                        checkDetected = False
                        #GPIO.output(22, 1) #Turn ON LED
                        time.sleep(1.5)
                        #GPIO.output(22, 0) #Turn OFF LED
                        numOfdetec = numOfdetec + 1
                        
                        if numOfdetec >= 2:
                            curDetecTime = datetime.datetime.now()
                            
                            returnTimeAction = curDetecTime - prevDetecTime
                            
                            next_state, reward, done, _ = self.getResult(action, returnTimeAction) #Get our reward for taking an action given a bandit.
                            
                            next_state = np.reshape(next_state, [1, self.state_size])
                            self.agent.remember(state, action, reward, next_state, done)
                            state = next_state
                            index += 1
                            #print(action)
                            
                        action = self.agent.act(state)
                        #print (json.dumps({"CorrentAction" : action + 1}))
                        #sys.stdout.flush()
                        if (action + 1) == 1: 
                            print (json.dumps({"action" : 1}))
                            sys.stdout.flush()
                            #sound_a() #It is a function for sound a!
                        elif (action + 1) == 2:
                            print (json.dumps({"action" : 2}))
                            sys.stdout.flush()
                            #sound_b()
                        elif (action + 1) == 3:
                            print (json.dumps({"action" : 3}))
                            sys.stdout.flush()
                            #sound_c()
                        elif (action + 1) == 4:
                            print (json.dumps({"action" : 4}))
                            sys.stdout.flush()
                            #sound_d()
                        
                        prevDetecTime = datetime.datetime.now()
                        #time.sleep(5)
                        
                    if self.welldone == False:
                        print (json.dumps({"iamdone" : 1}))
                        sys.stdout.flush()
                        time.sleep(1)
                                                
                    sys.stdout.flush()
                    time.sleep(0.001)
                #print("Episode {}# Score: {}".format(index_episode, index + 1))
                self.agent.replay(self.sample_batch_size)
        finally:
            self.agent.save_model()

if __name__ == "__main__":
    repeller = Repeller()
    repeller.run()

