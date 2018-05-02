# Imports.
import numpy as np
import numpy.random as npr
import pygame as pg

from SwingyMonkey import SwingyMonkey


class Learner(object):
    '''
    This agent jumps randomly.
    '''

    def __init__(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.gravity     = None

    def reset(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.gravity     = None
    
    def getvel(self,state):
        monkey = state.get("monkey")
        vel = monkey.get("vel")
        return vel
    
    def bottomcrashimpending(self,state):
        monkey = state.get("monkey")
        vel = monkey.get("vel")
        bot = monkey.get("bot")
        if bot + vel - self.gravity < 0:
            return 1
            print "fail"
        else:
            return 0
    
    def treecrashimpending(self,state):
        monkey = state.get("monkey")
        tree = state.get("tree")
        twidth = 115
        mwidth = 62
        mheight = 57
        xvel = 25
        yvel = monkey.get("vel")
        mtop = monkey.get("top")
        mbot = monkey.get("bot")
        dist = tree.get("dist")
        ttop = tree.get("top")
        tbot = tree.get("bot")
        t_remaining = (dist-215)/xvel
        #print t_remaining
        #print mbot, tbot
        #t_rf = dist - (mwidth)
        if (self.gravity == 4):
            if (t_remaining > -7):
                if (mbot + yvel - self.gravity < tbot):
                    return 1
                else:
                    return 0
            else:
                if (mbot + yvel - self.gravity < 100):
                    return 1
                else:
                    return 0
        else:
            if (t_remaining > -7):
                if (mbot + yvel - self.gravity < 0):
                    return 1
                if (mbot + yvel - self.gravity < tbot - 100):
                    return 1
                else:
                    return 0
            else:
                if (mbot + yvel - self.gravity < 0):
                    return 1
                else:
                    return 0
    

    def action_callback(self, state):
        '''
        Implement this function to learn things and take actions.
        Return 0 if you don't want to jump and 1 if you do.
        '''

        # You might do some learning here based on the current state and the last state.

        # You'll need to select and action and return it.
        # Return 0 to swing and 1 to jump.
        
        #start each game by learning the gravity
        #implicitly, take no action on the first time step
        if self.gravity == None:
            if self.last_state != None:
                #calculate the gravity
                self.gravity = self.getvel(self.last_state) - self.getvel(state)
        else:
            #jump if you are about to hit the bottom
            if self.bottomcrashimpending(state):
                new_action = 1
            #jump if your trajectory will lead to a collision with the bottom of the tree
            elif self.treecrashimpending(state):
                new_action = 1
            #otherwise pick your actions randomly
            else:
                new_action = 0
                #new_action = npr.rand() < 0.1
            
            #save the action that you took
            self.last_action = new_action
        
        #update the saved state
        self.last_state  = state
        
        #return the desired action
        return self.last_action

    def reward_callback(self, reward):
        '''This gets called so you can see what reward you get.'''

        self.last_reward = reward


def run_games(learner, hist, iters = 100, t_len = 100):
    '''
    Driver function to simulate learning by having the agent play a sequence of games.
    '''
    for ii in range(iters):
        # Make a new monkey object.
        swing = SwingyMonkey(sound=False,                  # Don't play sounds.
                             text="Epoch %d" % (ii),       # Display the epoch on screen.
                             tick_length = t_len,          # Make game ticks super fast.
                             action_callback=learner.action_callback,
                             reward_callback=learner.reward_callback)

        # Loop until you hit something.
        while swing.game_loop():
            pass
        
        # Save score history.
        hist.append(swing.score)

        # Reset the state of the learner.
        learner.reset()
    print hist
    pg.quit()
    return


if __name__ == '__main__':

	# Select agent.
	agent = Learner()

	# Empty list to save history.
	hist = []

	# Run games. 
	run_games(agent, hist, 20, 1)

	# Save history. 
	np.save('hist',np.array(hist))

