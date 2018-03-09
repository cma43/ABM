#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 17:05:37 2017

@author: Conor
"""

from enum import Enum
import math as math
import random as random
import weakref
import numpy as np

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
    _instances = set()
    
    class Role(Enum):
        CIVILIAN = 1
        CRIMINAL = 2
        POLICE = 3


    def __init__(self, x, y, of_type=None, resources = [], uid = None, network = None, hierarchy = None, history_self = [], history_others = [], policy=None, allies = [], competitors = [], crime_propensity=None):
        
        self.resources = resources
        self.uid = uid
        self.network = network
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
        self.memory = []
        self._instances.add(weakref.ref(self))
        self.num_times_robbed = 0
        
    @classmethod
    def getInstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead
        
        
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
        
    def distance(self,x1,x2,y1,y2):
        
        dist = math.sqrt((x1-x2)**2 + (y1-y2)**2) 
        return dist


    def dist(self, x2, y2):
        return math.sqrt((self.x-x2)**2 + (self.y-y2)**2)

 
    def look_for_agents(self, agent_role, cell_radius, agents_list):
        locations = []
        agent_list = []
        # Need to import aList from network class, or have the new environment class generate the list of agents

        #if agent_role is not 1 or 2 or 3:
        #    print("Please enter: CIVILIAN, CRIMINAL, or POLICE to select an agent role to search for.")
        #for agent in Agent.getInstances():
        #     agent_list.append(agent)
        # Iterate through each cell within cell_radius
        
        #civilian_list = [civilian for civilian in agent_list if civilian.role == Agent.Role.CIVILIAN]
        #police_list = [police for police in agent_list if police.role == Agent.Role.POLICE]
        #criminal_list = [criminals for criminals in agent_list if criminals.role == Agent.Role.CRIMINAL]

        civilian_location = []
        police_location = []
        criminal_location = []

        agents_in_sight = [agent for agent in agents_list if (agent.role == agent_role and
                                                              self.distance(self.x, agent.x, self.y, agent.y) <= cell_radius )]
        return agents_in_sight

        civilian_location = [civilian for civilian in civilian_list if self.distance(self.x, civilian.x, self.y, civilian.y) <= cell_radius]
        police_location = [police for police in police_list if self.distance(self.x, police.x, self.y, police.y) <= cell_radius]
        criminal_location = [criminal for criminal in criminal_list if self.distance(self.x, criminal.x, self.y, criminal.y) <= cell_radius] 

        if agent_role == Agent.Role.CIVILIAN:
            return civilian_location
        if agent_role == Agent.Role.CRIMINAL:
            return police_location
        if agent_role == Agent.Role.POLICE:
            return criminal_location

    def move(self, width, height, x=None, y=None, vision_radius=None):
        # This is from Zhen's code in crime.py
        # randomly move if memory is NULL


        # Nobblitt - addition for moving too specific location if specified - warning - no error checking
        if x is not None and y is not None:
            self.x, self.y = x, y
            return

        #if width or height is None:
            #print('Width or height invalid, please re-enter')

        if len(self.memory) == 0:
            while True:
                random.seed()
                d = random.sample([1, 2, 3, 4], 1)[0]
                if d == 1 and self.x > 0:
                    self.x += -1
                    return
                if d == 2 and self.y > 0:
                    self.y += -1
                    return
                if d == 3 and self.x < width:
                    self.x += 1
                    return
                if d == 4 and self.y < height:
                    self.y += 1
                    return

        # if memory is not NULL
        if len(self.memory) != 0:
            vision_radius = 2
            # Look for nearby criminals that we remember
            criminals_near = self.look_for_agents(agent_role=Agent.Role.CRIMINAL, agents_list=self.memory, cell_radius=vision_radius)

            # Possible directions to move in
            north, east, south, west = self.y < height, self.x < width, self.y > 0, self.x > 0
            # FIXME Replace Constant with Config for vision limit
            for criminal in criminals_near:
                # Essentially checking if distance is 1 in all cardinal directions
                if 0 < (criminal.y - self.y) <= vision_radius: north = False
                if -vision_radius <= (criminal.y - self.y) < 0: south = False
                if 0 < (criminal.x - self.x) <= vision_radius: east = False
                if -vision_radius <= (criminal.y - self.x) < 0: west = False

            # If north = True, it is possible to move north
            possible_directions = [north, east, south, west]


            try:
                # Choose a direction at random, given that it is possible
                weight = sum(possible_directions)
                if weight == 0 : return  # no where to go to
                direction = np.random.choice([1,2,3,4], 1, p=[x / weight for x in possible_directions])
                if direction == 1:
                    self.y += 1
                    return
                if direction == 2:
                    self.x += 1
                    return
                if direction == 3:  # South
                    self.y += -1
                    return
                if direction == 4: # West
                    self.x += -1
                    return
            except ValueError as e:
                print(str(e))
                # No where to move
                return
