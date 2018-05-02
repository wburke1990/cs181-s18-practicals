# Imports.
import numpy as np
import numpy.random as npr
import pygame as pg
from collections import defaultdict
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
        self.delta_pos = 50
        self.delta_rel_pos = 2
        self.delta_vel = 2
        self.delta_tree_bot = 5
        self.delta_dist = 25
        self.Q_dict = defaultdict(float)
        self.epoch       = 0
    
    def reset(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.gravity     = None
        self.epoch       = self.epoch + 1
    
    def getvel(self,state):
        monkey = state.get("monkey")
        vel = monkey.get("vel")
        return vel
    
    def get_key(self, state):
        '''
        This function takes the state and
        returns dictionary key based on binning
        the values of the state.
        '''
        
        k_g        = self.gravity
        k_vel      = int(state['monkey']['vel']/self.delta_vel)
        k_dist     = int(state['tree']['dist']/self.delta_dist)
        k_tree_bot = int(state['tree']['bot']/self.delta_tree_bot)
        
        if int(state['monkey']['bot']) + int(state['monkey']['vel']) - self.gravity > 0:
            k_pos = 1
        else:
            k_pos = 0

        if int(state['monkey']['bot']) > int(state['tree']['bot']):
            if (int(state['monkey']['bot']) + int(state['monkey']['vel']) - self.gravity > int(state['tree']['bot'])):
                k_rel_pos = 1
            else:
                k_rel_pos = 0
        else:
            k_rel_pos = -1

        # Current velocity
        v0 = state['monkey']['vel']

        # Current bottom position
        y0 = state['monkey']['bot']

        # Estimated time to hit tree.
        t_tree0 = (state['tree']['dist']-215)/25
        t_tree1 = (state['tree']['dist']-215)/25 + 5

        # Estimated height when at the tree.
        h_tree0 = y0 + v0*t_tree0 - 0.5*k_g*t_tree0*t_tree0

        # Estimated height when at the tree.
        h_tree1 = y0 + v0*t_tree1 - 0.5*k_g*t_tree1*t_tree1


        # Estimated height when at the tree.
        v_jump = 15
        h_tree_jump0 = y0 + v_jump*t_tree0 - 0.5*k_g*t_tree0*t_tree0
        h_tree_jump1 = y0 + v_jump*t_tree1 - 0.5*k_g*t_tree1*t_tree1

        monkey_height = 57

        if (int(h_tree0+monkey_height) > int(state['tree']['top'])) or (int(h_tree1+monkey_height) > int(state['tree']['top'])):
            k_tree_top = 0
        else:
            k_tree_top = 1

        if (int(h_tree0) > int(state['tree']['bot'])) or (int(h_tree1) > int(state['tree']['bot'])):
            k_tree_bot = 1
        else:
            k_tree_bot = 0


        if (int(h_tree_jump0+monkey_height) > int(state['tree']['top'])) or (int(h_tree_jump1+monkey_height) > int(state['tree']['top'])):
            k_tree_jump_top = 0
        else:
            k_tree_jump_top = 1

        if (int(h_tree_jump0) > int(state['tree']['bot'])) or (int(h_tree_jump1) > int(state['tree']['bot'])):
            k_tree_jump_bot = 1
        else:
            k_tree_jump_bot = 0

        #print(k_g, k_pos, k_rel_pos, k_dist, int(h_tree), state['tree']['bot'], state['tree']['top'], int(t_tree))

        if self.gravity == 1:
            return (k_pos, k_tree_bot, k_tree_top, k_tree_jump_bot, k_tree_jump_top)
            #return (k_pos, k_rel_pos, k_dist)
        elif self.gravity == 4:
            return (k_pos, k_tree_bot, k_tree_top, k_tree_jump_bot, k_tree_jump_top)
        else:
            print("Error calculating gravity: value is not acceptable. Acceptable values are 1 and 4")
            pg.quit()
    
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
            lastkey = self.get_key(self.last_state)
            key = self.get_key(state)
            epsilon = np.exp(-0.5*self.epoch)        
            jump_prob = 0.1
            #calculate the best action
            if self.Q_dict[key,1] > self.Q_dict[key,0]:
                Qmax = self.Q_dict[key,1]
                if npr.rand() < epsilon:
                    #pick a random action (most likely not a jump)
                    new_action = npr.rand() < jump_prob
                else:
                    #pick the best possible action
                    new_action = 1
            else:
                Qmax = self.Q_dict[key,0]
                if npr.rand() < epsilon:
                    #pick a random action (most likely not a jump)
                    new_action = npr.rand() < jump_prob
                else:
                    #pick the best possible action
                    new_action = 0

            #update the Q table
            #self.updateQ(state,Qmax,lastkey,)
            sample = self.last_reward + Qmax
            mu = 0.1
            Qold = self.Q_dict[lastkey,self.last_action]
            self.Q_dict[lastkey,self.last_action] = (1-mu)*Qold + mu*sample
            
            #update the saved state
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
        pg.quit()
        #print learner.gravity
        return


if __name__ == '__main__':
    
    # Select agent.
    agent = Learner()
    
    # Empty list to save history.
    hist = []
    
    # Run games.
    run_games(agent, hist, 100, 10)
    print(agent.Q_dict)
    print(hist)
    
    # Save history.
    np.save('hist',np.array(hist))
