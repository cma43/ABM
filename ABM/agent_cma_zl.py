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
from BWT_example import Building


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

    # Trick to limit RAM usage - but need to update if we add attributes
    __slots__ = ["resources", "uid", "network", "hierarchy", "history_self", "history_others", "policy", "allies",
                 "competitors", "role", "crime_propensity", "num_times_robbed", "memory", "residence"]

    def __init__(self, pos, model, resources, uid, network=None, hierarchy=None, history_self=[],
                 history_others=[], policy=None, residence=None):

        self.pos = pos
        self.environment = model
        self.resources = resources
        self.uid = uid

        # Optional vars
        self.network = network
        self.hierarchy = hierarchy
        self.history_self = history_self
        self.history_others = history_others
        self.policy = policy

        self.residence = residence
        if residence:
            residence.add_resident(self)


        # Data collection
        self.num_times_robbed = 0

    def __str__(self):
        return "Agent " + str(self.uid)

    def random_move(self):
        """Randomly walk around"""
        next_moves = self.environment.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        next_move = random.choice(next_moves)
        # Now move:
        self.environment.grid.move_agent(self, next_move)

    def random_move_and_avoid_role(self, role_to_avoid):
        """Randomly walk around, but not into cells with an agent of the specified role."""
        next_moves = self.environment.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        random.shuffle(next_moves)

        for cell in next_moves:
            agents = self.environment.grid.get_cell_list_contents(cell)
            has_police = sum([type(agent) is role_to_avoid for agent in agents])
            if not has_police:
                self.environment.grid.move_agent(self, cell)


    def walk_to(self, coordinates):
        """Walk one cell towards a set of coordinates, using only cardinal directions (North/South or West/East"""
        x, y = self.pos  # Current position
        x_target, y_target = coordinates  # Target position
        dx, dy = x_target - x, y_target - y  # Distance from target in terms of x/y

        # Scale dx/dy to -1/1 for use as coordinate move
        if dx != 0 and dy != 0:
            # Agent needs to go vertical and horizontally, choose one randomly
            if random.random() < 0.5:
                # Move horizontally
                dest_x = dx / abs(dx)
                dest_y = 0
            else:
                # Move vertically
                dest_y = dy / abs(dy)
                dest_x = 0
        elif dx == 0 and dy == 0:
            # Agent is at destination
            return True
        elif dx == 0:
            # Agent only needs to move vertically
            dest_y = dy / abs(dy)
            dest_x = 0
        elif dy == 0:
            # Agent only needs to move horizontally
            dest_x = dx / abs(dx)
            dest_y = 0

        # Add the picked direction to Agent's current position, now this is our destination cell
        dest_x, dest_y = int(dest_x + x), int(dest_y + y)

        self.environment.grid.move_agent(self, (dest_x, dest_y))
        # FIXME Check if there?
        return x_target == dest_x and y_target == dest_y


    def updateHistory_self(self, state, action, reward):
        # update its history which contains its state, action, reward and so on
        self.history_self = [self.history_self, [state, action, reward]]
        return self.history_self

    def updateHistory_others(self, states, actions, rewards):
        # update others' history which contains their states, actions, rewards and so on
        self.history_others = [self.history_others, [states, actions, rewards]]
        return self.history_others

    def die(self):
        pass
        # delete the agent under some conditions

    def set_residence(self, building):
        """Set the agent's residence to the specified building object"""
        assert(isinstance(building, Building))
        self.residence = building







