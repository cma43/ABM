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
    x = None
    y = None

    # Trick to limit RAM usage - but need to update if we add attributes
    __slots__ = ["resources", "uid", "network", "hierarchy", "history_self", "history_others", "policy", "allies",
                 "competitors", "role", "crime_propensity", "num_times_robbed", "memory"]

    def __init__(self, pos, model, resources, uid, network=None, hierarchy=None, history_self=[],
                 history_others=[], policy=None):

        self.pos = pos
        self.model = model
        self.resources = resources
        self.uid = uid

        # Optional vars
        self.network = network
        self.hierarchy = hierarchy
        self.history_self = history_self
        self.history_others = history_others
        self.policy = policy

        # Data collection
        self.num_times_robbed = 0

    def random_move(self):
        """Randomly walk around"""
        next_moves = self.model.grid.get_neighborhood(self.pos, True, include_center=True)
        next_move = random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)



    def walk_to(self, coordinates):
        """Walk one cell towards a set of coordinates"""
        x, y = self.pos
        x2, y2 = coordinates
        dx, dy = x2 - x, y2 - y

        dest_x, dest_y = 0, 0

        # Scale dx/dy to -1/1 for use as coordinate move
        if dx != 0 and dy != 0:
            # Agent needs to go vertical and horizontally, choose one randomly
            dx, dy = dx / abs(dx), dy / abs(dy)
            if random.random() < 0.5:
                dest_x = dx
            else:
                dest_y = dy
        elif dx == 0 and dy == 0:
            # Agent is at destination
            return True
        elif dx == 0:
            # Agent only needs to move vertically
            dest_y = dy / abs(dy)
        elif dy == 0:
            # Agent only needs to move horizontally
            dest_x = dx / abs(dx)

        # Add the picked direction to Agent's current position, now this is our destination cell
        dest_x, dest_y = int(dest_x + x), int(dest_y + y)

        self.model.grid.move_agent(self, (dest_x, dest_y))
        # FIXME Check if there?
        return x2 == dest_x + x and y2 == dest_y + y



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

    def distance(self, x1, x2, y1, y2):

        dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return dist

    def dist(self, x2, y2):
        return self.distance(self.x, x2, self.y, y2)

    def look_for_agents(self, agent_role, cell_radius, agents_list):

        agents_in_sight = [agent for agent in agents_list if (agent.role == agent_role and
                                                              self.distance(self.x, agent.x, self.y,
                                                                            agent.y) <= cell_radius)]
        return agents_in_sight

        civilian_location = [civilian for civilian in civilian_list if
                             self.distance(self.x, civilian.x, self.y, civilian.y) <= cell_radius]
        police_location = [police for police in police_list if
                           self.distance(self.x, police.x, self.y, police.y) <= cell_radius]
        criminal_location = [criminal for criminal in criminal_list if
                             self.distance(self.x, criminal.x, self.y, criminal.y) <= cell_radius]

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

        if len(self.memory) == 0:
            while True:
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

            # Look for nearby criminals that we remember
            criminals_near = self.look_for_agents(agent_role=Agent.Role.CRIMINAL, agents_list=self.memory,
                                                  cell_radius=vision_radius)

            # Possible directions to move in
            north, east, south, west = self.y < height, self.x < width, self.y > 0, self.x > 0
            # FIXME Replace Constant with Config for vision limit
            for criminal in criminals_near:
                # Essentially checking if distance is 1 in all cardinal directions
                if 0 < (criminal.y - self.y) <= vision_radius: north = False
                if -vision_radius <= (criminal.y - self.y) < 0: south = False
                if 0 < (criminal.x - self.x) <= vision_radius: east = False
                if -vision_radius <= (criminal.x - self.x) < 0: west = False

            # If north = True, it is possible to move north
            possible_directions = [north, east, south, west]

            try:
                # Choose a direction at random, given that it is possible
                weight = sum(possible_directions)
                if weight == 0: return  # no where to go to
                direction = np.random.choice([1, 2, 3, 4], 1, p=[x / weight for x in possible_directions])
                if direction == 1:
                    self.y += 1
                    return
                if direction == 2:
                    self.x += 1
                    return
                if direction == 3:  # South
                    self.y += -1
                    return
                if direction == 4:  # West
                    self.x += -1
                    return
            except ValueError as e:
                print(str(e))
                # No where to move
                return


class Criminal(Agent):
    def __init__(self, pos, model, resources=[], uid=None, network=None, hierarchy=None, history_self=[],
    history_others=[], policy=None, allies=[], competitors=[], crime_propensity=None):
        super().__init__(self, pos, model, resources, uid)
        self.pos = pos
        self.model = model
        self.resources = resources
        self.history_self = history_self
        self.history_others = history_others
        self.allies = allies
        self.competitors = competitors
        self.crime_propensity = crime_propensity
        self.vision = random.randint(1, model.config['agent_vision_limit'])

    def step(self):
        # Complete one time step
        potential_victim = self.look_for_victim()
        if potential_victim:
            # Found a victim with no police around
            if self.walk_to(potential_victim) and self.check_for_police():
                self.commit_crime()
                return

        self.random_move()
        return

    def commit_crime(self):
        """Commit a crime against a random agent in the current position"""
        # Get the agents in this cell
        potential_victims = self.model.grid.get_neighbors(pos=self.pos, moore=False, radius=0, include_center=True)

        # Find ourselves a victim
        victim = None
        for potential_victim in potential_victims:
            if type(potential_victim) is Civilian:
                victim = potential_victim
                break

        if victim is None:
            # No civilians in this cell
            return

        # Add criminal to victim's memory, regardless if successful
        victim.add_to_memory(self)

        # Rob Half of their resources if model deems it successful
        # This call to the model is an attempt to keep the environment in charge of interaction rules
        self.model.attempt_crime(self, victim)




    def look_for_victim(self):
        """Look in neighborhood for a civilian who is not protected by a nearby police.

        :return: Position of potential victim, if any
                 None, if not
        """
        neighbors = self.model.grid.get_neighbors(self.pos, False,  radius=self.vision, include_center=True)
        random.shuffle(neighbors)

        for agent in self.model.grid.get_neighbors(self.pos, False,  radius=self.vision, include_center=True):
            if type(agent) == Civilian:
                return agent.pos
        return False

    def check_for_police(self):
        """Check for police around a position, but only in cells the criminal can currently see in their neighborhood

        Params:
            pos (list): A list where [0] is x and [1] is y
            neighborhood (list): A list of cells, assumed to be the criminal's neighborhood
        Returns:
            True if there are police in proximity to pos that the Criminal can see in their neighborhood
        """

        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True, radius=self.vision)

        for neighbor in neighbors:
            if type(neighbor) is Police:
                return True

        return False

    def increase_propensity(self):
        """Increase the propensity of the criminal. Can be simple or maybe more complicated."""
        self.crime_propensity += 1
        return



class Civilian(Agent):
    def __init__(self, pos, model, resources=[], uid=None, network=None, hierarchy=None, history_self=[],
                 history_others=[], policy=None, allies=[], competitors=[]):
        super().__init__(self, pos, model, resources, uid, network, hierarchy, policy)
        self.pos = pos
        self.model = model
        self.resources = resources
        self.history_self = history_self
        self.history_others = history_others
        self.allies = allies
        self.competitors = competitors
        self.memory = list()
        self.vision = random.randint(1, model.config['agent_vision_limit'])

        # Individuals who have tried to rob this civilian
        self.criminal_memory = list()
        return

    def step(self):
        if len(self.memory) > 0:
            self.walk_and_avoid()
        else:
            self.random_move()
        return

    def walk_and_avoid(self):
        """Random walk, but avoid cells with agents

        Returns:
            True if successfully moved
            False if couldn't move anywhere
        """
        next_moves = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        random.shuffle(next_moves)

        for cell in next_moves:
            has_criminal = sum(agent in self.memory for agent in self.model.grid.get_cell_list_contents(cell))
            if not has_criminal:
                # has_criminal will be True if there are any criminals in the cell
                self.model.grid.move_agent(self, cell)
                return True

        return False

    def add_to_memory(self, agent):
        """Add a criminal to the civilian's memory, no repeats.

        params:
            agent (Agent): An agent that will be avoided in the future
        """
        self.memory.append(agent)
        self.memory = list(set(self.memory))  # remove repeats

        # Call police through the environment
        self.model.call_police(self, agent)
        return


class Police(Agent):
    """A Police Officer - an agent that is dispatched to Crime Scenes and arrests Evil Doers

    """

    def __init__(self, pos, model, resources=[], uid=None, network=None, hierarchy=None, history_self=[],
                 history_others=[], policy=None, allies=[], competitors=[]):
        super().__init__(self, pos, model, resources, uid, network, hierarchy, policy)
        self.pos = pos
        self.model = model
        self.resources = resources
        self.history_self = history_self
        self.history_others = history_others
        self.allies = allies
        self.competitors = competitors
        self.dispatch_coordinates = None
        self.target = None
        self.vision = random.randint(1, model.config['agent_vision_limit'])

    def step(self):
        """One time unit in the simulation, decide what actions to take"""

        # Check if this Police has an assignment
        if self.dispatch_coordinates is not None:
            if self.walk_to(self.dispatch_coordinates):
                self.initiate_investigation()
            # FIXME scan for target
            self.scan_for_target()
        else:
            # No dispatch assignment, patrol randomly
            self.random_move()

    def initiate_investigation(self):
        # Got to dispatch coordinates, check if target is in same cell
        print("Officer arrived at the crime scene")
        on_target = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=0)
        if on_target:
            if self.model.attempt_arrest(criminal=self.target, police=self):
                print("Boom! Criminal Arrested")

            # FIXME Take him to the station if caught

        elif not self.scan_for_target():
            # Drop Investigation
            self.drop_investigation()


    def drop_investigation(self):
        print("Officer could not find Criminal %s, they give up!" % self.target.uid)
        self.dispatch_coordinates = None


    def scan_for_target(self):
        # Check around officer if the target is in sight
        agents = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=self.vision)
        for agent in agents:
            if agent is self.target:
                self.dispatch_coordinates = agent.pos
                return True
            else:
                return False

class Coalition(object):
    """Parent class, A group of agents"""

    def __init__(self, environment):
        self.environment = environment
        self.members = list()

    def merge(self, other_coatlition):
        raise NotImplementedError

    def remove_member(self, agent):
        raise NotImplementedError

    def add_member(self, agent):
        raise NotImplementedError

class PoliceDepartment(Coalition):
    """A group of Police officers who coordinate together to stop EeeeeVIL"""

    def __init__(self, environment):
        super().__init__(environment)

    def dispatch(self, victim, target_agent):
        """Dispatch an officer to talk to a Civilian who called in about a robbery

        :param agent: The agent who called
        :return: None
        """
        officer = self.find_closest_free_officer(victim.pos)

        if officer is None:
            print("No available officers to dispatch")
            return False

        officer.dispatch_coordinates = victim.pos
        officer.target = target_agent
        print("Officer dispatched to Crime Scene")

    def find_closest_free_officer(self, pos):
        """Find the closest officer in the effective range of police officers"""
        police = self.environment.grid.get_neighbors(pos, moore=True,
                                                     include_center=True,
                                                     radius=self.environment.config['effective_police_radius'])
        police = list(filter(lambda x: type(x) is Police, police))

        random.shuffle(police)
        for officer in police:
            if officer.dispatch_coordinates is None:
                print(type(officer))
                return officer

