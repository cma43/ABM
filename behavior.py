# -*- coding: utf-8 -*-
"""

@author: conar
"""

from agents import Agent
from network import Network
from resources import Resources

class Behavior(object):
    
     """ A class for behavior modification in agents
    
    Attributes:
        uid: unique ID for agent
        network: The original network id where the agent is nested in 
        resources: The amount of each asset the agent has
        hierarchy: The level in organization (low, medium, high, etc)
        history_self, history_others: The agents' memory of history of itself and others
        policy: The agent's policy
        
    """
    
     def __init__(self, resources = [], states = [], policy):
        
       
        self.resources = resources
        self. states = states
        self.policy = policy
    

     def getUtility(self):
        #Function here for retrieving utility
        
        return self.utility
    
     def getPolicy(self, history):
        #Function here for retrieving policies
        
        return self.policy
        
     def getState(self):
        #Function here for retrieving states
        
        return self.state
        
     def getHistory(self, agentList):
         #...
         
         #Return the history of particular agent(s) in the form of a list of lists
         return history
 
     def utility(self, state, action):
        #...
        #return the instant or long-term reward if the initial state and the current action of the agent are given
        
        return profit
    
     def updatePolicy(self):
        #...
        #update the agent's policy based on some optimization criteria, history and so on 
        return self.policy

