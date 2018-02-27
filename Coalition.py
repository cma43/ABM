# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 11:39:58 2018

@author: zli34
"""


class Coalition(object):
    """A coalition in an organization/network
    Attributes:
        of_type: The type of the coalition
        members: List of agents in the coalition
        uid: unique ID for coalition
        network: The original network id where the coalition is nested in
        resources: The amount of each asset the coalition has
        history_self, history_others: The coalition's memory of history of itself and others
        policy: The coalition's policy
        competitors: The coalition's competitors
    """

    def __init__(self, of_type=None, members=[], resources=[], uid=None, network=None, history_self=[],
                 history_others=[], policy, competitors=[]):
        self.resources = resources
        self.uid = uid
        self.network = network
        self.history_self = history_self
        self.history_others = history_others
        self.policy = policy
        self.competitors = competitors

    def getUid(self):
        return self.uid

    def getResources(self):
        return self.resources

    def getNetwork(self):
        return self.network

    def getHistory_self(self):
        return self.history_self

    def getHistory_others(self):
        return self.history_others

    def getPolicy(self):
        return self.policy

    def updateHistory_self(self, state, action, reward):
        # update its history which contains its state, action, reward and so on
        self.history_self = [self.history_self, [state, action, reward]]
        return self.history_self

    def updateHistory_others(self, state, actions, rewards):
        # update others' history which contains their states, actions, rewards and so on
        self.history_others = [self.history_others, [states, actions, rewards]]
        return self.history_others

    def die(self):
# delete the coalition under some conditions
