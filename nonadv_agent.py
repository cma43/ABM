#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 17:05:37 2017

@author: Conor
"""

from agent import Agent

class Non_adversarialAgent(Agent):
    """A single non-adversarial agent in an organization/network
    
    Attributes:
        uid: unique ID for agent
        network: The original network id where the agent is nested in 
        resources: The amount of each asset the agent has
        hierarchy: The level in organization (low, medium, high, etc)
        history_self, history_others: The agents' memory of history of itself and others
        policy: The agent's policy
        allies: The allies of the agent
        neutrals: The neutrals of the agent
    """

    def __init__(self, x, y, resources = [], uid = None, network = None, hierarchy = None, history_self = [], history_others = [], policy, allies = [], neutrals = [], memory = []):
        
        super(Non_adversarialAgent, self).__init__(resources, uid, network, hierarchy, history_self, history_others, policy)       
        self.allies = allies
        self.neutrals = neutrals
        self.x = x
        self.y = y
        self.memory = memory
        
    def getAllies(self):
        return self.allies
    
    def getNeutrals(self):
        return self.neutrals
    
    def utility(self, state, action):
        #...
        #return the instant or long-term reward if the initial state and the current action of the agent are given
        return profit
    
    def utility(self, state):
        #...
        #return the instant or long-term reward if the initial state is given
        return profit
    
    def updatePolicy(self):
        #...
        #update the agent's policy based on some optimization criteria, history and so on 
        return self.policy
    
    def distance(x1,x2, y1, y2):
        
       dist =  math.sqrt((x1-x2)**2 + (y1-y2)**2)
       
       return dist
    
    def look_for_agents(self, agent_role, cell_radius, agent_list):
        locations = []
        #Need to import aList from network class, or have the new environment class generate the list of agents
        
        if agent_role is not 1 or 2 or 3:
            print("Please enter: CIVILIAN, CRIMINAL, or POLICE to select an agent role to search for.")

    	  #Iterate through each cell within cell_radius
        civilian_list = [civilian for cilivian in agent_list if civilian.Role == CIVILIAN]
        police_list = [police for police in agent_list if police.Role == POLICE]
        criminal_list = [criminals for criminals in agent_list if criminal.Role == CRIMINAL]

        civilian_location = []
        police_location = []
        criminal_location = []
        
        civilian_location = [civilian for civilian in civilian_list if distance(self.x, civilian.x, self.y, civilian.y) <= cell_radius]
        police_location = [police for police in police_list if distance(self.x, police.x, self.y, police.y) <= cell_radius]
        criminal_location = [criminal for criminal in criminal_list if distance(self.x, criminal.x, self.y, criminal.y) <= cell_radius]
            
            
        if agent_role == CIVILIAN:
            return civilian_location
        if agent_role == CRIMINAL:
            return police_location
        if agent_role == POLICE:
            return criminal_location
    
    def move(self,width,height):
        #This is from Zhen's code in crime.py
        #randomly move if memory is NULL
        
        if width or height is None:
            print('Width or height invalid, please re-enter')
            
        if len(self.memory)==0:
            while True:
                d=random.sample([1,2,3,4],1)[0]
                if d==1 and self.x-1>=0:
                    self.x=self.x-1
                    break
                if d==2 and self.y-1>=0:
                    self.y=self.y-1
                    break
                if d==3 and self.x+1<=width:
                    self.x=self.x+1
                    break
                if d==4 and self.y+1<=height:
                    self.y=self.y+1
                    break
        
        #if memory is not NULL
        if len(self.memory)!=0:
            a=[]
            for criminal in self.memory:
                if criminal.x>=math.floor(self.x)-1 and criminal.x<=math.floor(self.x) and criminal.y>=math.ceil(self.y) and criminal.y<=math.ceil(self.y)+1:
                    a.append([0,1,1,0])
                if criminal.x>=math.floor(self.x) and criminal.x<=math.floor(self.x)+1 and criminal.y>=math.ceil(self.y) and criminal.y<=math.ceil(self.y)+1:
                    a.append([1,1,1,0])
                if criminal.x>=math.ceil(self.x) and criminal.x<=math.ceil(self.x)+1 and criminal.y>=math.ceil(self.y) and criminal.y<=math.ceil(self.y)+1:
                    a.append([1,1,0,0])
                if criminal.x>=math.ceil(self.x) and criminal.x<=math.ceil(self.x)+1 and criminal.y>=math.floor(self.y) and criminal.y<=math.floor(self.y)+1:
                    a.append([1,1,0,1])
                if criminal.x>=math.ceil(self.x) and criminal.x<=math.ceil(self.x)+1 and criminal.y>=math.floor(self.y)-1 and criminal.y<=math.floor(self.y):
                    a.append([1,0,0,1])
                if criminal.x>=math.floor(self.x) and criminal.x<=math.floor(self.x)+1 and criminal.y>=math.floor(self.y)-1 and criminal.y<=math.floor(self.y):
                    a.append([1,0,1,1])
                if criminal.x>=math.floor(self.x)-1 and criminal.x<=math.floor(self.x) and criminal.y>=math.floor(self.y)-1 and criminal.y<=math.floor(self.y):
                    a.append([0,0,1,1])
                if criminal.x>=math.floor(self.x)-1 and criminal.x<=math.floor(self.x) and criminal.y>=math.floor(self.y) and criminal.y<=math.floor(self.y)+1:
                    a.append([0,1,1,1])
            
            
            b=[]
            for i in range(4):
                times=1
                for c in a:
                    times=c[i]*times
                b.append(times)
            
            if self.x-1<0:
                b[0]=0
                if self.y-1<0:
                    b[1]=0
                    if self.x+1>width:
                        b[2]=0
                        if self.y+1>height:
                            b[3]=0
                             
                
            count=0
            for i in b:
                if i==1:
                    count=count+1
                        
            d=random.sample(range(count),1)[0]
                
            e=0
            for i in b:
                if i==1 and e!=d:
                    b[i]=0
                    e=e+1
                        
            for i in range(4):
                if i==0:
                    self.x=self.x-b[i]
                if i==1:
                    self.y=self.y-b[i]
                if i==2:
                    self.x=self.x+b[i]
                if i==3:
                    self.y=self.y+b[i]
    
    
    
    
