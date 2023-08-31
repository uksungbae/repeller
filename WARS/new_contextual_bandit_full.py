import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import RPi.GPIO as GPIO
import time
import datetime
import pygame
import sys, json, select

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(8, GPIO.IN)         #Read output from 1 PIR motion sensor
GPIO.setup(10, GPIO.IN)         #Read output from 2 PIR motion sensor
GPIO.setup(12, GPIO.IN)         #Read output from 3 PIR motion sensor
GPIO.setup(22, GPIO.OUT)       #LED output pin

b = datetime.datetime.now()
rt = datetime.datetime.now() - b
checkDetected = False

#Initialise pygame and the mixer
pygame.init()
pygame.mixer.init()

#Json object checker for detected
def is_detected(obj):
    try:
        detected = obj['detected']
        sys.stdout.flush()
    except KeyError:
        return False
    return detected

#JSON format checker
def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError:
    return False
  return json_object

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
    
class contextual_bandit():
    def __init__(self):
        self.state = 0
        #List out our bandits. Currently arms 4, 2, and 1 (respectively) are the most optimal.
        self.bandits = np.array([[0,0,0,0]])
        self.num_bandits = self.bandits.shape[0]
        self.num_actions = self.bandits.shape[1]
        self.bandits_rt = np.array([[rt,rt,rt,rt]])

    def getBandit(self):
        self.state = np.random.randint(0,len(self.bandits)) #Returns a random state for each episode.
        return self.state

    def pullArm(self, action, result):
        #Get a random number.
        bandit = self.bandits[self.state,action]
        #print("bandit: " + str(bandit))
        #result = np.random.randn(1)
        #result = float(input("Please enter the R/T: "))
        #print("RT: " + str(self.bandits_rt[s,action]))
        
        if result > self.bandits_rt[s,action]:
            #return a positive reward.
            self.bandits_rt[s,action] = result
            return 1
        else:
            #return a negative reward.
            self.bandits_rt[s,action] = result
            return -1

class agent():
    def __init__(self, lr, s_size,a_size):
        #These lines established the feed-forward part of the network. The agent takes a state and produces an action.
        self.state_in= tf.placeholder(shape=[1],dtype=tf.int32)
        state_in_OH = slim.one_hot_encoding(self.state_in,s_size)
        output = slim.fully_connected(state_in_OH,a_size,\
        biases_initializer=None,activation_fn=tf.nn.sigmoid,weights_initializer=tf.ones_initializer())
        self.output = tf.reshape(output,[-1])
        self.chosen_action = tf.argmax(self.output,0)
        
        #The next six lines establish the training proceedure. We feed the reward and chosen action into the network
        #to compute the loss, and use it to update the network.
        self.reward_holder = tf.placeholder(shape=[1],dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[1],dtype=tf.int32)
        self.responsible_weight = tf.slice(self.output,self.action_holder,[1])
        self.loss = -(tf.log(self.responsible_weight)*self.reward_holder)
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=lr)
        self.update = optimizer.minimize(self.loss)
        
try:
    time.sleep(1)
    numOfdetec = 0
    
    tf.reset_default_graph() #Clear the Tensorflow graph.

    cBandit = contextual_bandit() #Load the bandits.
    myAgent = agent(lr=0.001,s_size=cBandit.num_bandits,a_size=cBandit.num_actions) #Load the agent.
    weights = tf.trainable_variables()[0] #The weights we will evaluate to look into the network.

    total_reward = np.zeros([cBandit.num_bandits,cBandit.num_actions]) #Set scoreboard for bandits to 0.
    e = 0.3 #Set the chance of taking a random action.

    init = tf.global_variables_initializer()

    # Launch the tensorflow graph
    with tf.Session() as sess:
        sess.run(init)
        while True:
            input = getLine();
            if(input != False):
                json_object = is_json(input)
                if(json_object != False):
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
                    #print (json.dumps({"PreviousDate" : prevDetecTime, "CurrentDate" : curDetecTime, "ReturningTime" : curDetecTime - prevDetecTime, "PreviusAction" : action + 1}))
                    #sys.stdout.flush()
                    result = curDetecTime - prevDetecTime
                                                       
                    reward = cBandit.pullArm(action, result) #Get our reward for taking an action given a bandit.
                    #print("Mean reward: " + str(bandits[self.state,action]))
                    
                    #Update the network.
                    feed_dict={myAgent.reward_holder:[reward],myAgent.action_holder:[action],myAgent.state_in:[s]}
                    _,ww = sess.run([myAgent.update,weights], feed_dict=feed_dict)
                    
                    #Update our running tally of scores.
                    total_reward[s,action] += reward
                    #print (ww)
                    #if i % 1 == 0:
                    #print ("Mean reward for each of the " + str(cBandit.num_bandits) + " bandits: " + str(total_reward))
                    
                    
                s = cBandit.getBandit() #Get a state from the environment.
                #Choose either a random action or one from our network.
                if np.random.rand(1) < e:
                    action = np.random.randint(cBandit.num_actions)
                else:
                    action = sess.run(myAgent.chosen_action,feed_dict={myAgent.state_in:[s]})
                    
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
                                
            time.sleep(0.001)
            #sys.stdout.flush()
except:
    GPIO.cleanup()