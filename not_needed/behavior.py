# -*- coding: utf-8 -*-
"""

@author: conar
"""

from bwt_agents import Agent
from environ_config import environ as env
from scipy.optimize import fmin  

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
        #Function for retrieving utility: 
        
        
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
         
         #Compute utility for a given agent. 
         
         if(self.env.config['utility_function_type'] == 'type_1'):
             #Perfect substitution between inputs
             U = alpha*x + (1-alpha)*y
             
        
         if(self.env.config['utility_function_type'] == 'type_2'):
             #No subsitution between inputs
             U = min(alpha*x, (1-alpha)*y)
             
             
         if(self.env.config['utility_function_type'] == 'type_3'):
             #Unit elasticity between inputs
             U = (x^alpha)*(y^(1-alpha))
             
         
         #If the agent is a criminal:
         if isinstance(self, Criminal):
              
             #Criminals in BWT get utility from gaining resources from victims,
             #acquiring more buildings in their grid environment, and not getting
             #caught by the police. 
             
             
             
             
             return 
         
         #If the agent is a civilian:
         if isinstance(self, Civilian):
             return NotImplementedError

         #If the agent is police:
         if isinstance(self, Police):
             return NotImplementedError
         
        
        #return the instant or long-term reward if the initial state and the current action of the agent are given
        
        
    
     def updatePolicy(self):
        #...
        #update the agent's policy based on some optimization criteria, history and so on 
        return self.policy

