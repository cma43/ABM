#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 17:05:37 2017

@author: Conor
"""

class AdversarialAgent(Agent):
    """A single adversarial agent in an organization/network
    
    Attributes:
        uid: unique ID for agent
        network: The original network id where the agent is nested in 
        resources: The amount of each asset the agent has
        hierarchy: The level in organization (low, medium, high, etc)
        classes: The class of the agent
        history_self, history_others: The agents' memory of history of itself and others
        policy: The agent's policy
        allies: The allies of the agent
        neutrals: The neutrals of the agent
        competitors: The competitors of the agent
    """

    def __init__(self, resources = [], uid = None, network = None, hierarchy = None, history_self = [], history_others = [], policy, allies = [], neutrals = [], competitors = []):        
        super(AdversarialAgent, self).__init__(resources, uid, network, hierarchy, history_self, history_others, policy)
        self.allies = allies
        self.neutrals = neutrals
        self.competitors = competitors
    
    def getAllies(self):
        return self.allies
    
    def getNeutrals(self):
        return self.neutrals
    
    def getCompetitors(self):
        return self.competitors
    
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
