#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 17:05:37 2017

@author: Conor
"""

from enum import Enum

class Agent(object):
    """A single agent in an organization/network
    
    Attributes:
        uid: unique ID for agent
        network: The original network id where the agent is nested in 
        resources: The amount of each asset the agent has
        hierarchy: The level in organization (low, medium, high, etc)
        history_self, history_others: The agents' memory of history of itself and others
        policy: The agent's policy
        allies: The agent's allies
        competitors: The agent's competitors
        
        
    """
    class Role(Enum):
        CIVILIAN = 1
        CRIMINAL = 2
        POLICE = 3


    def __init__(self, x, y, of_type=None, resources = [], uid = None, network = None, hierarchy = None, history_self = [], history_others = [], policy=None, allies = [], competitors = [], crime_propensity=None):
        
        self.resources = resources
        self.uid = uid
        self.network = network
        if network is not None:
            network.members.append(self)
        self.hierarchy = hierarchy
        self.history_self = history_self
        self.history_others = history_others
        self.policy = policy
        self.allies = allies
        self.competitors = competitors
        self.x = x
        self.y = y
        self.role = of_type
        self.crime_propensity = crime_propensity
        
        
    def getUid(self):
        return self.uid
    
    def getResources(self):
        return self.resources
    
    def getNetwork(self):
        return self.network
    
    def getHierarchy(self):
        return self.hierarchy
    
    def getHistory_self(self):
        return self.history_self
    
    def getHistory_others(self):
        return self.history_others
    
    def getPolicy(self):
        return self.policy
    
    def updateHistory_self(self, state, action, reward):
        #update its history which contains its state, action, reward and so on 
        self.history_self = [self.history_self, [state, action, reward]]
        return self.history_self
        
    def updateHistory_others(self, states, actions, rewards):
        #update others' history which contains their states, actions, rewards and so on
        self.history_others = [self.history_others, [states, actions, rewards]]
        return self.history_others
            
    def die(self):
        pass
        #delete the agent under some conditions

    def look_for_agents(self, agent_role, cell_radius, agent_list):
        locations = []
        # Need to import aList from network class, or have the new environment class generate the list of agents

        if agent_role is not 1 or 2 or 3:
            print("Please enter: CIVILIAN, CRIMINAL, or POLICE to select an agent role to search for.")

        # Iterate through each cell within cell_radius
        civilian_list = [civilian for civilian in agent_list if civilian.Role == Agent.Role.CIVILIAN]
        police_list = [police for police in agent_list if police.Role == Agent.Role.POLICE]
        criminal_list = [criminals for criminals in agent_list if criminals.Role == Agent.Role.CRIMINAL]

        civilian_location = []
        police_location = []
        criminal_location = []

        civilian_location = [civilian for civilian in civilian_list if
                             distance(self.x, civilian.x, self.y, civilian.y) <= cell_radius]
        police_location = [police for police in police_list if
                           distance(self.x, police.x, self.y, police.y) <= cell_radius]
        criminal_location = [criminal for criminal in criminal_list if
                             distance(self.x, criminal.x, self.y, criminal.y) <= cell_radius]

        if agent_role == CIVILIAN:
            return civilian_location
        if agent_role == CRIMINAL:
            return police_location
        if agent_role == POLICE:
            return criminal_location

    def move(self, width, height):
        # This is from Zhen's code in crime.py
        # randomly move if memory is NULL

        if width or height is None:
            print('Width or height invalid, please re-enter')

        if len(self.memory) == 0:
            while True:
                d = random.sample([1, 2, 3, 4], 1)[0]
                if d == 1 and self.x - 1 >= 0:
                    self.x = self.x - 1
                    break
                if d == 2 and self.y - 1 >= 0:
                    self.y = self.y - 1
                    break
                if d == 3 and self.x + 1 <= width:
                    self.x = self.x + 1
                    break
                if d == 4 and self.y + 1 <= height:
                    self.y = self.y + 1
                    break

        # if memory is not NULL
        if len(self.memory) != 0:
            a = []
            for criminal in self.memory:
                if criminal.x >= math.floor(self.x) - 1 and criminal.x <= math.floor(
                        self.x) and criminal.y >= math.ceil(self.y) and criminal.y <= math.ceil(self.y) + 1:
                    a.append([0, 1, 1, 0])
                if criminal.x >= math.floor(self.x) and criminal.x <= math.floor(
                        self.x) + 1 and criminal.y >= math.ceil(self.y) and criminal.y <= math.ceil(self.y) + 1:
                    a.append([1, 1, 1, 0])
                if criminal.x >= math.ceil(self.x) and criminal.x <= math.ceil(self.x) + 1 and criminal.y >= math.ceil(
                        self.y) and criminal.y <= math.ceil(self.y) + 1:
                    a.append([1, 1, 0, 0])
                if criminal.x >= math.ceil(self.x) and criminal.x <= math.ceil(self.x) + 1 and criminal.y >= math.floor(
                        self.y) and criminal.y <= math.floor(self.y) + 1:
                    a.append([1, 1, 0, 1])
                if criminal.x >= math.ceil(self.x) and criminal.x <= math.ceil(self.x) + 1 and criminal.y >= math.floor(
                        self.y) - 1 and criminal.y <= math.floor(self.y):
                    a.append([1, 0, 0, 1])
                if criminal.x >= math.floor(self.x) and criminal.x <= math.floor(
                        self.x) + 1 and criminal.y >= math.floor(self.y) - 1 and criminal.y <= math.floor(self.y):
                    a.append([1, 0, 1, 1])
                if criminal.x >= math.floor(self.x) - 1 and criminal.x <= math.floor(
                        self.x) and criminal.y >= math.floor(self.y) - 1 and criminal.y <= math.floor(self.y):
                    a.append([0, 0, 1, 1])
                if criminal.x >= math.floor(self.x) - 1 and criminal.x <= math.floor(
                        self.x) and criminal.y >= math.floor(self.y) and criminal.y <= math.floor(self.y) + 1:
                    a.append([0, 1, 1, 1])

            b = []
            for i in range(4):
                times = 1
                for c in a:
                    times = c[i] * times
                b.append(times)

            if self.x - 1 < 0:
                b[0] = 0
                if self.y - 1 < 0:
                    b[1] = 0
                    if self.x + 1 > width:
                        b[2] = 0
                        if self.y + 1 > height:
                            b[3] = 0

            count = 0
            for i in b:
                if i == 1:
                    count = count + 1

            d = random.sample(range(count), 1)[0]

            e = 0
            for i in b:
                if i == 1 and e != d:
                    b[i] = 0
                    e = e + 1

            for i in range(4):
                if i == 0:
                    self.x = self.x - b[i]
                if i == 1:
                    self.y = self.y - b[i]
                if i == 2:
                    self.x = self.x + b[i]
                if i == 3:
                    self.y = self.y + b[i]