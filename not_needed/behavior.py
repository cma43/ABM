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
 
     def computeUtility(self, buildings, civilians, police):
         
         #Compute utility for a given agent after passing a list of buildings, police
         #and civilians to it after looking within an agent's vision limit
          
         if(self.env.config['utility_function_type'] == 'type_1'):
             #Perfect substitution between inputs
             
             def U(x, y):
                 U = alpha*x + (1-alpha)*y
             
        
         if(self.env.config['utility_function_type'] == 'type_2'):
             #No subsitution between inputs
             def U(x, y):
                 U = min(alpha*x, (1-alpha)*y)
             
             
         if(self.env.config['utility_function_type'] == 'type_3'):
             #Unit elasticity between inputs
             def U(x, y):
                 U = (x^alpha)*(y^(1-alpha))
             
         
         #If the agent is a criminal:
         if isinstance(self, Criminal):
              
             #Criminals in BWT get utility from gaining resources from victims,
             #acquiring more buildings in their grid environment, and not getting
             #caught by the police. 
             
             #Look at all possible current resources
             
             #TODO Agents should not be able to perfectly see all resources.
             #TODO There should be some risk probability for being arrested
             
             x = [civilian.resources[-1] for civilian in civilians]
             y = [building.attractiveness[-1] for building in buildings]
             
             
             #TODO compute and add in cost of travel to get to agents and buildings 
             # along with the chance of being caught
             criminal_utility = U(x,y) - travelCost - riskCost
             
             
             return criminal_utility
         
         #If the agent is a civilian:
         if isinstance(self, Civilian):
             
             #Civilians get utility from completing their routes and going to work
             #coming back home in as little time as possible. (This means they evaluate
             #the minimum distance between their endpoints under the constraint that they 
             #want to avoid 'bad areas' and criminals as they go.)
             
             #They get disutility from being robbed or attacked, and
             #from incurring risks by walking through 'bad areas'.
             
             civilian_utility = U(x,y) - travelCost - riskCost
             
             return NotImplementedError

         #If the agent is police:
         if isinstance(self, Police):
             
             #Police get utility from stopping crimes, catching criminals, and pursuing
             #criminals. They get disutility from failing to catch criminals, failing 
             #to stop crimes, or getting killed by criminals. 
             
             police_utility = U(x,y) - travelCost - riskCost
             
             return NotImplementedError
         
        
        #return the instant or long-term reward if the initial state and the current action of the agent are given
        
     def computeTotalUtility(self, agent):
         
         #This computes total utility up until present time-step for the agent
         
         #TODO Ideally agents should saved their most recently computed expected utility
         #     and then update that previous estimate in a sequential average 
         
         utility_list = [agent.utility[i]*(kappa)^i for i in len(agent.utility)]
         total_discounted_utility = sum(utility_list)
         
         return total_discounted_utility
        
        
    
     def updatePolicy(self):
        #...
        #update the agent's policy based on some optimization criteria, history and so on 
        return self.policy

