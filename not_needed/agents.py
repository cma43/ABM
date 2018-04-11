#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 17:05:37 2017

@author: Conor
"""


import random 
import numpy as np

agents = []


class Agent(object):
    """A single agent in an organization/network


    Attributes:
        uid: unique ID for agent
        network: The original network id taht the agent is nested in 
        asset: The amount of each asset the agent has
        hierarchy: level in organization (low, medium, hogh, etc)
        coal: 1 if in a coalition with another network or agent and 0 o/w
        
       
        Maybe: 
        Maybe: coal: 1 if in a coalition with another network or agent and 0 o/w
        
    """

    
    #For simplest case, give a random endownment an agent starts with here or
    #a zero endowment for all agents:
    n_agents = 3
     
    
    

    def __init__(self, coal, asset = [], uid = None, network=None, hierarchy = None):
        
        self.uid = uid
        self.coal = 0
        self.network = network
        self.asset = []
        self.hierarchy = hierarchy
        
        self.info_score = 0 #0 if you don't have better information, 1 if you do
        self.init_asset = random.gauss(1, 1)
        self.threshold = .15*(self.init_asset)
        self.asset.append(self.init_asset)
        
    def __repr__(self):
        return self.uid
    
    #def __str__(self):
     #   return self.uid #For potentially printing Agent() instances
    
    def expectedReturn(self, rounds):
  
         #Calculate expected asset return for some # rounds ahead
         estimates = [np.random.normal(1.0, 1.0, rounds) for i in range(rounds) ]
         guess = np.mean(estimates)
    
         return guess
     
    def coalitionReturn(self, rounds):
  
        #Calculate expected asset return for some # rounds ahead
        estimates = [np.random.normal(.75, .25, rounds) for i in range(rounds) ]
        guess = np.mean(estimates)
    
        return guess
     
    def coerce(self, otherAgent):
        eps = .05
        luck = np.random.uniform(0,1)
        
        if(otherAgent.asset[-1] < otherAgent.threshold):
            if luck > eps:
                otherAgent.coal = 1
                self.coal = 1
                print("Agent coerced")
                return True
        
            if luck <= eps:
                self.coal = 0
                otherAgent.coal = 0
                print("Coercion attempt failed")
                return False 
        
        if(otherAgent.asset[-1] >= otherAgent.threshold):
            if luck > eps:
                print("Agent not coerced")
                return False
        
            if luck <= eps:
                self.coal = 1
                otherAgent.coal = 1
                print("Coerced anyway")
                return True 
        
    def joinCoalition(self, otherAgent):
        
        eps = .2
        luck = np.random.uniform(0,1)
        
        #Implement inside of a list comprehension to loop through combinations
        #of agents
        
        #Agent simulates average of 5 rounds ahead -- if > current asset,
        #will want to join a coalition to hedge bets 
        
        #If expected to go under, join coalition; if currently below
        #lowest threshold, also join coalition (work through logical if/else
        #contingences)
        
        if(otherAgent.asset[-1] + otherAgent.expectedReturn(3) < otherAgent.threshold ):
            self.coal = 1
            otherAgent.coal = 1
            return True 
        
            if luck <= eps:
                self.coal = 0
                otherAgent.coal = 0
                print("Coalition attempt failed")
                return False 
            
        if(otherAgent.asset[-1] + otherAgent.expectedReturn(3) < 0):
            self.coal = 1
            otherAgent.coal = 1
            return True 
        
            if luck <= eps:
                self.coal = 0
                otherAgent.coal = 0
                print("Coalition attempt failed")
                return False
        
        if(otherAgent.expectedReturn(5) < otherAgent.coalitionReturn(3)):
            if luck > eps:
                self.coal = 1
                otherAgent.coal = 1
                return True 
        
            if luck <= eps:
                self.coal = 0
                otherAgent.coal = 0
                print("Coalition attempt failed")
                return False 
            
        if(otherAgent.asset[-1] + otherAgent.expectedReturn(3) >= otherAgent.threshold):
            
            if luck > eps:
                self.coal = 0
                otherAgent.coal = 0
                return False
        
            if luck <= eps:
                self.coal = 1
                otherAgent.coal = 1
                print("Accidentally started coalition!")
                return True
           
        
        #(Insert combinations of if's that say 'if one needs it but not the
        #other, if both need it, if the other one needs it but not the other,
        #etc.')
        
        #(Use this function in an 'if' statement search about for other agents) 
        
        #if self.asset[-1] + self.expectedReturn(5) < 0:
        

            
    def die(self):
        
        #Remove or delete agent from list or dictionary of agents
        #Call this first, then if agent passes this, moves on to 
        #joinCoalition function
        
        #if agent's assets < 0, agent dies
       
        if not self.asset: #If the list of assets is empty, raise an error
                raise Exception("No assets available yet!")
          
        if (self.asset[-1] < 0):
        #In case you want to kill off agents which are beneath their threshold:
        #just append this statement to the if statement above: 
        #or (self.asset[-1] < self.threshold):
            #If assets are negative, return
            #true to pass to the network's dead() function, which will then
            #remove that agent from the network
                print('Agent is going to die!')
                return True     

        

    def step(self):
     eps = .05
     luck = np.random.uniform(0,1)
        #Could include an 'if <0 then dead' statement for testing here
        
        #Look at all agents. If they are below their own threshold, 
        #put them aside. These agents can be 'coerced' -- whoever gets to them
        #first gets to assign them to a coalition. If two agents are below
        #their threshold value, then the choosing agent picks only one. If 
        #there's only one agent below threshold, then randomly pick which of 
        #the other two agents gets to coerce.
        
        #IF( not in coalition ):
        #Adjust each agent’s wealth / income / assets by += N(1,1) — could also 
        #change to N(1,theta) with theta ~ U(0,1)
        
     if not self.asset:
         
        raise Exception("No assets available yet!")
         
     if self.coal == 0:
       
       if self.info_score == 0:  
        largeV = np.random.uniform(1,5) 
        print("Not in coalition")
        
        if luck > eps:
            self.asset.append(self.asset[-1] + np.random.normal(1.0, largeV))
        if luck <= eps: 
            self.asset.append(self.asset[-1] - np.random.normal(1.0, largeV))
       if self.info_score == 1:
           print("Not in coalition")
           if luck > eps:
            self.asset.append(self.asset[-1] + np.random.normal(1.0, 1.0))
           if luck <= eps: 
            self.asset.append(self.asset[-1] - np.random.normal(1.0, 1.0))

     if self.coal == 1:
       if self.info_score == 0:  
        smallV = np.random.uniform(.25, 1) 
        print("In coalition")
        if luck > eps:
            self.asset.append(self.asset[-1] + np.random.normal(.75, smallV))
        if luck <= eps:
            self.asset.append(self.asset[-1] - np.random.normal(.75, smallV))
       if self.info_score == 1:
        if luck > eps:
            self.asset.append(self.asset[-1] + np.random.normal(.75, .25))
        if luck <= eps:
            self.asset.append(self.asset[-1] - np.random.normal(.75, .25))

      

      
    #@abstractmethod
    #def agent_type(self):
    #    """"Return a string representing the type of agent this is."""
    #    pass