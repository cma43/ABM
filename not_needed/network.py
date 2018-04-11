#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 10:27:28 2017

@author: Conor
"""

import networkx as nx
import matplotlib.pylab as plt
from not_needed.agents import Agent
import itertools
import random





"""
Later: Should include conditions in functions checking how many other agents
are left to compete against agent-wise or network-wise
"""

class Network(object):
    
    def __init__(self, N): 
        
        self.N = N
        self.aList = []
        self.G=nx.OrderedMultiDiGraph()
        self.adjM = []
        
        #initializing the number of agents requested
        for i in range(N):
            agent = Agent(self)
            agent.uid = i
            self.aList.append(agent)
            
        #selecting random agent from list of agents to have a simple information "advantage"    
        lucky_agent = random.choice(self.aList)
        lucky_agent.info_score = 1
        print("Agent " + str(lucky_agent.uid) + " has more info")
        self.lucky_agent_id = lucky_agent.uid
            
            
    
    def populate(self):
            #Create node #'s that correspond to Unique ID numbers after
            #generating agents 
            
            #First attempt: 
            #G.add_nodes_from(agents) #(later may change to n_agents)
            
            
            #This assigns our agent's unique ID as labels for each node:
        for agent in self.aList:
            self.G.add_node(agent.uid) 
            
            #Update adjacency matrix and print to console 
        self.adjM.append(nx.adjacency_matrix(self.G))
        print(self.adjM)
            
            #Draw and plot the updated graph
        nx.draw_networkx(self.G)
        plt.show()
            
        return self.adjM
        
            
            
            
    def checkCoalition(self):
        
        #(Note: you need to update the coalition aspect to reflect that 
        #coalitions are specific to a particular agent/network in the future)
            
            #Checks the status of pairs of agents, and if returns true,
            #then forms an edge between the two agents' nodes:
            
            #Micellaneous piece of code that may help later:
            #[x for x in myList if x.n == 30] 
            
            #Later will need to make this efficient for examining
            #many pairs of agents because we'll have 2^k comparisons
            #to make for k agents in the simulation
            
            #There will be two nodes, u and v. Assign each node
            #the same Uniqued ID (uid) that generated the nodes and
            #which correspond to the node's number. 
                
        coalList = [agent for agent in self.aList if agent.coal==1]        
                
        if(len(coalList) < 2):
            print("No coalitions!")
            return False
        if(len(coalList) > 1):
            
            for agent in coalList:
            
                u = agent[0].uid
                v = agent[1].uid


            if(agent[0].coal==1 & agent[1].coal==1):
                self.G.add_edge(u,v)
                self.adjM.append(nx.adjacency_matrix(self.G))
                return True 
            if(agent[0].coal==0 or agent[1].coal==0):
                if(self.G.has_edge(u,v)==True):
                    self.G.remove_edge(u,v)
                    self.adjM.append(nx.adjacency_matrix(self.G))
                    return False
                if(self.G.has_edge(u,v)==False):
                    return False 
            
    
                
                
    def dead(self):
            
        #Simple criteria for agents interacting and dying based solely on resources 
        #(From initial simple ABM )
        
        
        for agent in self.aList:
                
            if(agent.die() == True):
                u = agent.uid
                #removing node
                self.G.remove_node(u)
                self.aList.remove(agent)
                nx.draw_networkx(self.G, with_labels=True)
                plt.show()
                print("Agent died!")
                
                
        self.adjM.append(nx.adjacency_matrix(self.G))
        return self.adjM
    
    def updateGraph(self):
        # Method for updating placement and coloring of agents in a network graph
        
        self.adjM.append(nx.adjacency_matrix(self.G))
        pos = nx.spring_layout(self.G)
        
        color_map = []
        for node in self.G:
            if self.lucky_agent_id == node:
                color_map.append('blue')
            else: color_map.append('red')  
                    
        
        nx.draw_networkx(self.G, pos = pos, node_color = color_map, with_labels=True)
        plt.show()
        
    def add_rand(self):
        
        #Function that was previously used for testing how to add agents to a network:
        
        #Adds a random agent to the network
       u =   random.randint(0, 2)
       v =   random.randint(0, 2)
       
       if(u!=v):
           self.G.add_edge(u,v)
           self.updateGraph()
    
    def rem_rand(self):
        
        #Function that was previously used for testing how to add agents to a network:
        
        #Randomly removes an agent from the network

        u =  random.randint(0, 2)
        v =  random.randint(0, 2)
        
        node = [0,1,2]
        
        nodes = itertools.combinations(node, r = 2)

        for node in nodes:
            if(self.G.has_edge(node[0], node[1])):
                self.G.remove_edge(u,v)
                self.updateGraph()
                
    def checkCoercion(self):
        print("Start statement")
        agentList = itertools.combinations(self.aList, r = 2)
        print("Agent list made")

        for agent in agentList:
            print("For loop started")

            if(agent[0].coerce(agent[1])):
                print("Coercion between agents")
                self.G.add_edge(agent[0].uid, agent[1].uid)
                
                self.adjM.append(nx.adjacency_matrix(self.G))
                
                nx.draw_networkx(self.G, with_labels=True)
                plt.show()
                
            #if(pair[0].coerce(pair[1])) is False:
                #print("No coercion between agents")
       
  
        

                
                

