#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 17:05:37 2017

@author: Conor
"""


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

    def __init__(self, resources = [], uid = None, network = None, hierarchy = None, history_self = [], history_others = [], policy, allies = [], competitors = []):
        
        self.resources = resources
        self.uid = uid
        self.network = network       
        self.hierarchy = hierarchy
        self.history_self = history_self
        self.history_others = history_others
        self.policy = policy
        self.allies = allies
        self.competitors = competitors
        
    def getUid(self):
        return self.uid
    
    def getResources(self):
        return self.resources
    
    def getNetwork(self):
        return self.network
    
    def getHierarchy(self):
        return self.hierarchy
    
    def getClasses(self):
        return self.classes
    
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
        
    def updateHistory_others(self, state, actions, rewards):
        #update others' history which contains their states, actions, rewards and so on
        self.history_others = [self.history_others, [states, actions, rewards]]
        return self.history_others
            
    def die(self):
        pass
        #delete the agent under some conditions
        
    
    
