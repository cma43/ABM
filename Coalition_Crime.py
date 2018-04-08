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


# from environ_config import environ as environ

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

    def __init__(self, of_type=None, members=[], resources=[], uid=None, network=None, history_self=[],
                 history_others=[], policy=None, competitors=[], x=0, y=0, combined_crime_propensity=0):
        Coalition.__init__(self, of_type=of_type, members=members, resources=resources, uid=uid, network=network,
                           history_self=history_self, history_others=history_others, policy=policy,
                           competitors=competitors)
        self.x = x
        self.y = y
        self.combined_crime_propensity = combined_crime_propensity

    def move_together(self, width, height, x=None, y=None, vision_radius=None, civilians=None):
        if x is not None and y is not None:
            self.x, self.y = x, y
            for member in self.members:
                member.x, member.y = x, y
            return
        if len(self.members[0].look_for_agents(agent_role=Agent.Role.CIVILIAN, cell_radius=vision_radius,
                                               agents_list=civilians)) == 0:
            while True:
                d = random.sample([1, 2, 3, 4], 1)[0]
                if d == 1 and self.x > 0:
                    return self.move_together(width, height, x=self.x-1, y=self.y)
                if d == 2 and self.y > 0:
                    return self.move_together(width, height, x=self.x, y=self.y-1)
                if d == 3 and self.x < width:
                    return self.move_together(width, height, x=self.x+1, y=self.y)
                if d == 4 and self.y < height:
                    return self.move_together(width, height, x=self.x, y=self.y+1)

        else:
            # search for civilians within the coalition's vision radius
            victims = self.members[0].look_for_agents(agent_role=Agent.Role.CIVILIAN, cell_radius=vision_radius,
                                                      agents_list=civilians)

            # search for the nearest civilians within the coalition's vision radius
            dist = self.members[0].distance(self.x, victims[0].x, self.y, victims[0].y)
            nearest_victims = []
            for victim in victims:
                if self.members[0].distance(self.x, victim.x, self.y, victim.y) < dist:
                    nearest_victims = [victim]
                    dist = self.members[0].distance(self.x, victim.x, self.y, victim.y)
                elif self.members[0].distance(self.x, victim.x, self.y, victim.y) == dist:
                    nearest_victims.append(victim)

            # choose one from the nearest civilians randomly as the goal
            victim = nearest_victims[random.sample(range(len(nearest_victims)), 1)[0]]

            # move towards the goal
            dist = self.members[0].distance(self.x - 1, victim.x, self.y, victim.y)
            move = [1]
            if self.members[0].distance(self.x, victim.x, self.y - 1, victim.y) < dist:
                move = [2]
                dist = self.members[0].distance(self.x, victim.x, self.y - 1, victim.y)
            elif self.members[0].distance(self.x, victim.x, self.y - 1, victim.y) == dist:
                move.append(2)
            if self.members[0].distance(self.x + 1, victim.x, self.y, victim.y) < dist:
                move = [3]
                dist = self.members[0].distance(self.x + 1, victim.x, self.y, victim.y)
            elif self.members[0].distance(self.x + 1, victim.x, self.y, victim.y) == dist:
                move.append(3)
            if self.members[0].distance(self.x, victim.x, self.y + 1, victim.y) < dist:
                move = [4]
            elif self.members[0].distance(self.x, victim.x, self.y + 1, victim.y) == dist:
                move.append(4)

            while True:
                d = move[random.sample(range(len(move)), 1)[0]]
                if d == 1 and self.x > 0:
                    self.x += -1
                    for i in self.members:
                        i.x += -1
                    return
                if d == 2 and self.y > 0:
                    self.y += -1
                    for i in self.members:
                        i.y += -1
                    return
                if d == 3 and self.x < width:
                    self.x += 1
                    for i in self.members:
                        i.x += 1
                    return
                if d == 4 and self.y < height:
                    self.y += 1
                    for i in self.members:
                        i.y += 1
                    return

    def merge_with_coalition(self, other_coalition, threshold_propensity):
        '''
        Merges other_coalition into this coalition, if possible. Returns True for successful merge, otherwise false
        :param other_coalition: The coalition that will be absorbed
        :param threshold_propensity: The global propensity required to commit crimes
        :return:
        '''
        if self.can_merge_with_coalition(other_coalition, threshold_propensity):
            for member in other_coalition.members:
                member.x = self.x
                member.y = self.y
                self.members.append(member)
                self.combined_crime_propensity += member.crime_propensity
            del other_coalition
            return True
        return False

    def can_merge_with_coalition(self, other_coalition, threshold_propensity):
        return self.combined_crime_propensity < threshold_propensity and other_coalition.combined_crime_propensity < threshold_propensity

    def commit_crime(self, civilians, police, threshold, crime_radius, vision_radius):
        potential_victims = self.can_commit_crime(crime_radius=crime_radius, vision_radius=vision_radius,
                                                 threshold=threshold, civilians=civilians, police=police)
        if potential_victims:
            # There are nearby civilians and no police
            victim = random.choice(potential_victims)
            booty = victim.resources[0] = 0.5 * victim.resources[0]

            victim.memory += list(set(self.members) - set(victim.memory))
            victim.num_times_robbed += 1

            self.move_together(None, None, victim.x, victim.y)

            for member in self.members:
                member.resources[0] += booty / len(self.members)
                member.crime_propensity += 1
                self.combined_crime_propensity += 1

            return [victim.x, victim.y]
        else:
            return False

    def can_commit_crime(self, crime_radius, vision_radius, threshold, civilians, police):
        # FIXME Temporary fix to ensure propensity is updated - remove later for efficiency's sake
        self.update_propensity()
        if self.combined_crime_propensity < threshold:
            return False

        potential_victims = self.members[0].look_for_agents(agent_role=Agent.Role.CIVILIAN, cell_radius=crime_radius,
                                                            agents_list=civilians)

        if len(potential_victims) == 0:
            return False

        # of_type = 2 means police
        if len(self.members[0].look_for_agents(agent_role=Agent.Role.POLICE, cell_radius=vision_radius,
                                               agents_list=police)) > 0:
            return False

        return potential_victims

    def update_propensity(self):
        """
        Helper class to update the combined_propensity variable
        :return: void
        """

        if len(self.members) == 0:
            self.combined_crime_propensity = 0

        else:
            self.combined_crime_propensity = 0
            for member in self.members:
                self.combined_crime_propensity += member.crime_propensity

    def distance(self, other_coalition):
        dist = math.sqrt((self.x - other_coalition.x) ** 2 + (self.y - other_coalition.y) ** 2)
        return dist

