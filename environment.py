import config.environ_config as cfg
import numpy as np
import random
from Coalition_Crime import Coalition_Crime
from agent_cma_zl import Criminal, Civilian, Police, PoliceDepartment
import matplotlib.pyplot as plt
import copy
from collections import namedtuple
from mesa import space
from mesa import time



class Environment(object):
    '''
    A contained environment, describes a space and the rules for interaction
    between agents and resources. Can be spatial (grid-like) or non-spatial (nodes and connections).
    '''

    def __init__(self, uid, spatial=True):
        '''
        Constructor
        :param:
        '''

        # Unique Environment ID
        self.uid = uid

        # Load Environment config
        self.config = cfg.environ

        # Initial population parameters
        self.population_counts = {
            'civilians': self.config['num_civilians'],
            'criminals': self.config['num_criminals'],
            'police':  self.config['num_police']
        }

        # Grid from mesa
        self.grid = space.MultiGrid(width=self.config['grid_width'],
                                    height=self.config['grid_height'],
                                    torus=True)

        # Scheduler from Mesa
        self.scheduler = time.RandomActivation(self)

        self.agents = {
            'civilians' : list(),
            'criminals' : list(),
            'police' : list()
        }

        # Police Department
        self.pd = PoliceDepartment(self)

        # FIXME To be implemented
        # History of resources
        self.resourceHistory = []


    def run(self, num_steps):
        """Run one batch for the desired number of steps"""
        self.populate()

        for step in range(num_steps):
            self.tick()
            self.plot()

    def plot(self):
        fig, ax = plt.subplots()
        ax.scatter([agent.pos[0] for agent in self.agents['civilians']],
                   [agent.pos[1] for agent in self.agents['civilians']],
                   color="red",
                   alpha=0.5)
        ax.scatter([agent.pos[0] for agent in self.agents['criminals']],
                   [agent.pos[1] for agent in self.agents['criminals']],
                   color="green",
                   alpha=0.5)
        ax.scatter([agent.pos[0] for agent in self.agents['police']],
                   [agent.pos[1] for agent in self.agents['police']],
                   color="blue",
                   alpha=0.5)
        #ax.scatter([agent.pos[0] for agent in self.scheduler.agents], [agent.pos[1] for agent in self.scheduler.agents])
        plt.show()


    def tick(self):

        self.scheduler.step()

        # FIXME add data collection


    def get_expected_resource(self):
        raise NotImplementedError


    def populate(self):
        '''
        Initiate random population placement onto spatial grid
        Populates global list of all agents, all criminals, all civilians, all police, each with their own list
        :return:
        '''

        # Add criminals
        for criminal_id in range(self.population_counts['criminals']):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            criminal = Criminal(pos=(x, y),
                                model=self,
                                resources=[random.randrange(self.config['initial_resource_max'])],
                                uid=criminal_id,
                                crime_propensity=random.randrange(self.config['initial_crime_propensity_max']))
            self.grid.place_agent(pos=criminal.pos, agent=criminal)
            self.agents['criminals'].append(criminal)
            self.scheduler.add(criminal)

        # Populate Civilians
        for civilian_id in range(self.population_counts['civilians']):
            civilian = Civilian(pos=(random.randrange(0, self.grid.width), random.randrange(0, self.grid.height)),
                                model=self,
                                resources=[random.randrange(self.config['initial_resource_max'])],
                                uid=civilian_id)
            self.grid.place_agent(pos=civilian.pos, agent=civilian)
            self.agents['civilians'].append(civilian)
            self.scheduler.add(civilian)


        # Populate Police
        for police_id in range(self.population_counts['police']):
            police = Police(pos=(random.randrange(0, self.grid.width), random.randrange(0, self.grid.height)),
                              model=self,
                              resources=[random.randrange(self.config['initial_resource_max'])],
                              uid=police_id)
            self.grid.place_agent(pos=police.pos, agent=police)
            self.agents['police'].append(police)
            self.scheduler.add(police)
            self.pd.members.append(police)


    def attempt_crime(self, criminal, victim):
        """Determines if a crime is successful
        """
        # Probability of success - replace with any equation, e.g. including crime propensity
        p = 0.5

        # Add criminal to victim's memory, regardless of crime outcome
        victim.add_to_memory(criminal)

        if random.random() < p:
            # Successful crime, take resources from victim
            print("Crime was successful at %s" % str(victim.pos))
            criminal.resources[0] += victim.resources[0]/2
            victim.resources[0] /= 2

            # increase criminal's propensity
            criminal.increase_propensity()

    def attempt_arrest(self, criminal, police):
        """Determines if an arrest is successful"""
        p = 0.5
        return random.random() < p

    def call_police(self, victim, agent):
        """Call the police, give them a description of the criminal.

        params:
            agent (Criminal): The criminal that the police should look out for
        """
        self.pd.dispatch(victim, agent)
