#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Sep  5 17:11:30 2017

@author: Conor
"""

import random
import importlib as importlib

from not_needed import agents, network

importlib.reload(agents)
importlib.reload(network)

from not_needed.network import Network

if __name__=='__main__':

    'Working out functions and how they work/should be called:'
    
    #Create a network with k=3 agents in it 
    n = Network(7)    
    n.populate() 
        
    #n.updateGraph()
    
    
    while(len(n.aList) > 2):
    

    #Check if any agents are already dead/if they started
    #with a bad initial random endowment by chance:  
    
        n.dead()
    
    #Randomly check between agents for coercion:
    
    #Search list for coercible agent, store that agent somewhere if available,
    #then randomly pick between the two other available agents:
    
        coercibles = [agent for agent in n.aList if agent.asset[-1] < agent.threshold]
    
        if not coercibles:
            print("No coercible agents!")
            n.updateGraph()

        if(len(coercibles) > 0):
        
        #print(*coercibles, sep='\n')
        
            randAgents = [agent for agent in n.aList if agent not in coercibles]
        
            agent1 = random.choice(randAgents)
            agent2 = random.choice(coercibles)
        
            n.updateGraph()

            for agent in coercibles:
                if(len(coercibles) == 0):
                    n.updateGraph()
                    continue
                if(agent1.coerce(agent2)):
                    n.G.add_edge(agent1.uid, agent2.uid)
                    n.updateGraph()
                    coercibles.remove(agent2)
                

    #Check between agents for voluntarily joining coalition because of 
    #low threshold, update if coalition forms
    
        for agent in n.aList:
            if(agent.expectedReturn(3) + agent.asset[-1] <= agent.threshold):
            
                if(agent.coal == 1):
                #Stop, because already in coalition, and go to next agent
                    n.updateGraph()

                    continue 
            
                if(agent.coal == 0):
                #Search for other agents, join if expected return is good
                    temp = [agent]
                
                    potentialCoals = [agents for agents in n.aList not in temp]
                
                    for newAgent in potentialCoals:
                        if(agent.joinCoalition(newAgent)):
                            n.G.add_edge(agent.uid, newAgent.uid)
                            n.updateGraph()
                
                #Later may want to select all pairwise combinations:
                #potentialCoals = itertools.combinations(n.aList, r = 2) 
    
    #Next, have each agent receive their next endowment
    
    # In case we want to randomize order before 
    # next step/asset gain in future:  
    
    #n.checkCoalition()
        
        for agent in n.aList:
            agent.step()
            
            
        
    

    
    
    
