# -*- coding: utf-8 -*-
"""

@author: conar
"""
from agent_cma_zl import Agent
from bwt_agents import Criminal, Civilian, Police
from Building import Building
from environ_config import environ as env
from scipy.optimize import fmin  
from scipy.spatial.distnace import euclidean

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
 
     def computeUtility(self, agents, pos):
         
         #Compute utility for a given agent after passing a list of buildings, police
         #and civilians to it after looking within an agent's vision limit
          
         #TODO Different types of agents shouldn't necessarily have the same 
         # utility function
         
         
         if(self.env.config['utility_function_type'] == 'type_1'):
             #Perfect substitution between inputs
             
             def U(x):
                 U = env.config['alpha']*x #+ (1-env.config['alpha'])*y
                 
        
         if(self.env.config['utility_function_type'] == 'type_2'):
             
             def U(x, y):
                 U = min(env.config['alpha']*x, (1-env.config['alpha'])*y)
                 
             
         if(self.env.config['utility_function_type'] == 'type_3'):
             #Unit elasticity between inputs
             def U(x, y):
                 U = (x^env.config['alpha'])*(y^(1-env.config['alpha']))
                 
         
         #If the agent is a criminal:
         #if isinstance(self, Criminal):
              
             #Criminals in BWT get utility from gaining resources from victims,
             #acquiring more buildings in their grid environment, and not getting
             #caught by the police. 
             
             #Look at all possible current resources
             
             #TODO Agents should not be able to perfectly see all resources.
             #TODO There should be some risk probability for being arrested
             
             dist = [euclidean(pos, agent) for agent in agents]
             value = []
             
             for agent in agents:
                 if isinstance(agent, Civilian):
                     value.append(U(agent.resources[-1]))
                 elif isinstance(agent, Building): 
                     value.append(U(agent.attractiveness[-1]))
                     
             criminal_utility = value - dist
             
             #TODO compute and add in cost of travel to get to agents and buildings 
             # along with the chance of being caught
             
            
             return criminal_utility
         
         #If the agent is a civilian:
        # if isinstance(self, Civilian):
             
             #Civilians get utility from completing their routes and going to work
             #coming back home in as little time as possible. (This means they evaluate
             #the minimum distance between their endpoints under the constraint that they 
             #want to avoid 'bad areas' and criminals as they go.)
             
             #They get disutility from being robbed or attacked, and
             #from incurring risks by walking through 'bad areas'.
             
             #x = [civilian.resources[-1] for civilian in civilians]
             
            # civilian_utility = U(x,y) 
             
             #return civilian_utility

         #If the agent is police:
        # if isinstance(self, Police):
             
             #Police get utility from stopping crimes, catching criminals, and pursuing
             #criminals. They get disutility from failing to catch criminals, failing 
             #to stop crimes, or getting killed by criminals. 
             
             #x = [civilian.resources[-1] for civilian in civilians]
             
            # police_utility = U(x,y) 
             
             #return police_utility
         
        
        #return the instant or long-term reward if the initial state and the current action of the agent are given
     def getVictimLocation(self, criminal_utility_list, agents):
        #Returns position of the agent the criminal will pursue. 
        criminal_utility_max = max(criminal_utility_list)
        victim_index = criminal_utility_list.index(criminal_utility_max)
        
        victim_position = agents[victim_index].pos
        return victim_position
        
     def computeTotalUtility(self, agent):
         
         #This computes total utility up until present time-step for the agent
         
         #TODO Ideally agents should saved their most recently computed expected utility
         #     and then update that previous estimate in a sequential average 
         
         utility_list = [agent.utility[i]*(kappa)^i for i in len(agent.utility)]
         total_discounted_utility = sum(utility_list)
         
         return total_discounted_utility
        
     def computeCost(self, agent):
         
         #Compute a cost function for criminals
         
         #TODO Generalize to other agent types
         
         
         
         
         return NotImplementedError
        
    
     def updatePolicy(self):
        #...
        #update the agent's policy based on some optimization criteria, history and so on 
        return self.policy

