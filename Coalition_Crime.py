# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 13:41:36 2018

@author: zli34
"""
import math
import numpy as np
import random
from Coalition import Coalition
from agent_cma_zl import Agent

class Coalition_Crime(Coalition):
    """A subclass of Coalition
    Attributes:
        of_type: The type of the coalition
        members: List of agents in the coalition
        uid: unique ID for coalition
        network: The original network id where the coalition is nested in 
        resources: The amount of each asset the coalition has
        history_self, history_others: The coalition's memory of history of itself and others
        policy: The coalition's policy
        competitors: The coalition's competitors
        
        location
        combined_crime_propensity
    """
    def __init__(self, of_type = None, members = [], resources = [], uid = None, network = None, history_self = [], history_others = [], policy=None, competitors = [], x=None, y=None, combined_crime_propensity=None):
        Coalition.__init__(self, of_type = of_type, members=members, resources=resources, uid =uid, network=network,
                           history_self=history_self, history_others=history_others, policy=policy, competitors=competitors)
        self.x = x
        self.y = y
        self.combined_crime_propensity = combined_crime_propensity
    
    def move_together(self):
        while True:
            d = random.sample([1,2,3,4],1)[0]
            if d == 1 and self.x-1 >= 0:
                self.x = self.x-1
                for i in self.members:
                    i.x = i.x-1
                break
            if d == 2 and self.y-1 >= 0:
                self.y = self.y-1
                for i in self.members:
                    i.y = i.y-1
                break
            if d == 3 and self.x+1 <= self.network.width:
                self.x = self.x+1
                for i in self.members:
                    i.x = i.x+1
                break
            if d == 4 and self.y+1 <= self.network.height:
                self.y = self.y+1
                for i in self.members:
                    i.y = i.y+1
                break
        
        
    def merge_with_coalition(self, other_coalition):
        if can_merge_with_coalition(self, other_coalition):
            for member in other_coalition.members:
                self.members.append(member)
                self.combined_crime_propensity += 1
            del other_coalition
        
        
    def can_merge_with_coalition(self, other_coalition):
        return self.crime_propensity < self.network.threshold_propensity and other_coalition.crime_propensity < network.threshold_propensity
    
    def commit_crime(self):
        if self.can_commit_crime(self):
            #of_type = 1 means civilian
            #Agent.cell_radius needs to be modified
            victims = self.members[0].look_for_agent(of_type = 1, cell_radius = Agent.cell_radius) 
            
            victim = random.sample(victims,1)[0]
            victim.resources[0] = 0.5*victim.resources[0]
            
            #history_others means a civilian's memory
            victim.history_others = victim.history_others + self.members
            #remove the same elements in memory
            #victim.memory=[set(victim.memory)]
            
            for member in self.members:
                member.resources[0] += victim.resources[0] / len(self.members)
                member.crime_propensity += 1
                self.combined_crime_propensity += 1          
                
    def can_commit_crime(self):
        if self.combined_crime_propensity < self.network.threshold_propensity:
            return False
        
        #of_type = 1 means civilian
        #Agent.cell_radius needs to be modified
        if len(self.members[0].look_for_agent(of_type = 1, cell_radius = Agent.cell_radius)) == 0:
            return False
        
        #of_type = 2 means police
        if len(self.members[0].look_for_agent(of_type = 3, cell_radius = Agent.cell_radius)) > 0:
            return False
        
        return True
        
        