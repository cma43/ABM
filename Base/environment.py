
import Examples.BWT.config.environ_config as cfg
from mesa import space
from mesa import time
#from mesa.datacollection import DataCollector
#from data_collector import DataManager
from Examples.BWT.MapGenerator import MapGenerator

from Examples.BWT.Building import Building, CommercialBuilding
from Examples.BWT.Police_Department import *
from Examples.BWT.bwt_agents import Police, Criminal, Civilian
from Base.Coalition_Crime import Coalition_Crime


#matplotlib.use("TkAgg")
import tkinter as tk
from tkinter import ttk
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from IPython import get_ipython
import matplotlib.pyplot as plt


import numpy as np
import copy
import random 
import functools
import logging

#import os 
#print(os.environ.get('QT_API'))


LARGE_FONT = ("Verdana", 12)


#plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(0, cfg.environ['grid_width'])
ax.set_ylim(0, cfg.environ['grid_height'])
#get_ipython().run_line_magic('matplotlib', 'qt')

class Environment(object):
    '''
    A contained environment, describes a space and the rules for interaction
    between agents and resources. Can be spatial (grid-like) or non-spatial (nodes and connections).
    '''

    def __init__(self, uid):
        '''
        Constructor
        :param: uid (int): The unique id for this environment
        '''
        
        # Unique Environment ID
        self.uid = uid

        # Load Environment config
        self.config = cfg.environ
        
        # Initial population counts
        self.population_counts = {
            'civilians': self.config['num_civilians'],
            'criminals': self.config['num_criminals'],
            'police':    self.config['num_police']
        }

        # Mesa grid where agent overlap is possible
        # FIXME make toolable for user
        self.grid = space.MultiGrid(width=self.config['grid_width'],
                                    height=self.config['grid_height'],
                                    torus=False)

        # Scheduler from Mesa
        # FIXME Make toolable for user
        self.schedule = time.RandomActivation(self)

        # Agent Information
        self.agents = {
            # List of all agents
            'civilians': list(),
            'criminals': list(),
            'police': list(),
            'residences': list(),
            'roads': list(),
            'commercial_buildings': list()
        }

        self.next_building_id = 0

        self.next_criminal_uid = len(self.agents['criminals'])

        # Coalition Information
        self.criminal_coalitions = list()
        self.next_coalition_uid = 0

        # Data Collection variables
        self.total_crimes = 0
        self.total_arrests = 0
        self.total_coalitions = 0

        # TODO make static function
        mg = MapGenerator(self)
        mg.generate_map()


        # TODO implement
        # History of resources
        self.resourceHistory = []
        
        #ax.set_xlim(-2, self.grid.width)
        #ax.set_ylim(-2, self.grid.height)
        #get_ipython().run_line_magic('matplotlib', 'qt')
        ani = animation.FuncAnimation(fig, self.plot, interval = 100, repeat = True)
        #plt.show()
       
        
    def tick(self):
        """One step of the simulation. Calls pre-step which calculates/executes any necessary environment changes before
         agent actions are deliberated/executed."""

        self.pre_step()
        self.schedule.step()

        # Testing an arbitrarily increasing threshold to mimic adversarial interactionss
        #self.config['crime_propensity_threshold'] *= 0.02

    def plot(self):
         """Draw the environment and the agents within it."""
         
        #get_ipython().run_line_magic('matplotlib', 'qt')
    
    # Plot roads
         ax.cla()
         ax.scatter([building.pos[0] for building in self.agents['commercial_buildings']],
                           [building.pos[1] for building in self.agents['commercial_buildings']],
                           color="blue", marker="s", zorder=1)
        
         ax.scatter([road.pos[0] for road in self.agents['roads']],
                           [road.pos[1] for road in self.agents['roads']],
                           color="grey", marker="s", zorder=1)
        
         ax.scatter([building.pos[0] for building in self.agents['residences']],
                           [building.pos[1] for building in self.agents['residences']],
                           color="black", marker="s", zorder=1)
        
         ax.scatter([agent.pos[0] for agent in self.agents['civilians']],
                           [agent.pos[1] for agent in self.agents['civilians']],
                           color="green",
                           alpha=.9,
                           zorder=3)
        
         ax.scatter([agent.pos[0] for agent in self.agents['criminals']],
                           [agent.pos[1] for agent in self.agents['criminals']],
                           color="red",
                           alpha=.9,
                           zorder=3)
         ax.scatter([agent.pos[0] if agent.dispatch_coordinates is not None else None for agent in self.agents['police']],
                           [agent.pos[1] if agent.dispatch_coordinates is not None else None for agent in self.agents['police']],
                           color="blue",
                           alpha=0.95,
                           zorder=3)
         ax.scatter([agent.pos[0] if agent.dispatch_coordinates is None else None for agent in self.agents['police']],
                           [agent.pos[1] if agent.dispatch_coordinates is None else None for agent in self.agents['police']],
                           color="blue",
                           alpha=0.7,
                           zorder=3)
        
        
         if getattr(self, "pd", None):
            ax.scatter(self.pd.pos[0], self.pd.pos[1],
                               color="black",
                               marker="+")
                   
                   
         
         plt.pause(.2)
         plt.show()
         
    def pre_step(self):
        """Do any necessary actions before letting agents move.

          Stabilizes building attractiveness across the grid,
          Adds new criminals if arrest_behavior = "remove".
        """

        # Stabilise building attractivnesss
        for building in self.agents['residences']:
            self.improve_building_attractiveness(building)

        if self.config['arrest_behavior'] == "imprison":
            # No pre_step necessary
            return

        # Drop a random number of criminals on the map
        num = np.random.poisson(self.config['lambda'])
        for i in range(num):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            new_agent = BWT_example.bwt_agents.Criminal(uid=self.next_criminal_uid,
                                 model=self,
                                 pos=(x,y),
                                 resources=[random.randrange(self.config['initial_resource_max'])],
                                 crime_propensity=random.randrange(self.config['initial_crime_propensity_max']))
            self.grid.place_agent(pos=new_agent.pos, agent=new_agent)
            self.agents['criminals'].append(new_agent)
            self.schedule.add(new_agent)
            logging.info("Criminal " + str(new_agent.uid) + " enters the grid.")
            self.next_coalition_uid += 1

    def get_expected_resource(self):
        raise NotImplementedError

    def populate(self):
        '''Initiate random population placement onto grid.

        Populates global list of all agents, all criminals, all civilians, all police, each with their own list
        '''

        # Add criminals
        for criminal_id in range(self.population_counts['criminals']):

            criminal = Criminal(pos=(self.random_road_pos()),
                                model=self,
                                resources=[random.randrange(self.config['initial_resource_max'])],
                                uid=criminal_id,
                                crime_propensity=random.randrange(self.config['initial_crime_propensity_max']),
                                workplace = self.random_commercial_building(),
                                residence=self.random_residence())

            self.grid.place_agent(pos=criminal.pos, agent=criminal)

            self.agents['criminals'].append(criminal)
            # self.schedule.add(criminal)
            self.schedule._agents[criminal.uid] = criminal

        # Populate Civilians
        for civilian_id in range(self.population_counts['criminals'], self.population_counts['criminals'] + self.population_counts['civilians']):
            # Create a civilian and their new house (which is in a random location on the grid)

            civilian = Civilian(pos=self.random_road_pos(),
                                model=self,
                                resources=[random.randrange(self.config['initial_resource_max'])],
                                uid=civilian_id,
                                residence=self.random_residence(),
                                workplace=self.random_commercial_building(),
                                )
            self.grid.place_agent(pos=civilian.pos, agent=civilian)  # Place civilian on grid
            self.agents['civilians'].append(civilian)
            # self.schedule.add(civilian)
            self.schedule._agents[civilian.uid] = civilian
        
        

        # Populate Police
        self.pd = PoliceDepartment(uid=1, environment=self)

        for police_id in range(self.population_counts['criminals'] + self.population_counts['civilians'], self.population_counts['criminals']
        + self.population_counts['civilians'] + self.population_counts['police']):
            police = Police(pos=(random.randrange(0, self.grid.width), random.randrange(0, self.grid.height)),
                              model=self,
                              resources=[random.randrange(self.config['initial_resource_max'])],
                              uid=police_id)
            self.grid.place_agent(pos=police.pos, agent=police)
            police.pd = self.pd
            self.agents['police'].append(police)
            # self.schedule.add(police)
            self.schedule._agents[police.uid] = police
            self.pd.members.append(police)
        
        print("Finish populating!")

    def random_road_pos(self):
        """Returns a random cell where a road exist"""
        return self.agents['roads'][random.randrange(0, len(self.agents['roads']))].pos

    def random_residence(self):
        """Returns a random residence"""
        return self.agents['residences'][random.randrange(0, len(self.agents['residences']))]

    def random_commercial_building(self):
        """Returns a random commercial residence"""
        return self.agents['commercial_buildings'][random.randrange(0, len(self.agents['commercial_buildings']))]

    def attempt_arrest(self, criminal, police):
        """Determines if an arrest is successful"""

        if random.random() < self.config['police_arrest_probability']:
            logging.info("{0} Arrested".format(str(criminal)))
            self.total_arrests += 1
            criminal.crime_propensity -= 0.5

            if self.config['arrest_behavior'] == 'imprison':
                self._imprison_criminal(criminal, police)
            elif self.config['arrest_behavior'] == 'remove':
                self._remove_criminal(criminal, police)

            # Make sure other police are no longer looking for the same target
            self.pd.remove_target(criminal)
            return True
        else:
            logging.info("Arrest attempt failed!")
            # FIXME Patience timer?
            return False
        

    def crime_wrapper(crime_function):
        """Controls whether a crime is successful."""

        @functools.wraps(crime_function)
        def inner_wrapper(self, *args, **kwargs):
            if random.random() < self.config['crime_success_probability']:
                self.total_crimes += 1
                crime_function(self, *args, **kwargs)
        return inner_wrapper

    @crime_wrapper
    def attempt_violent_crime(self, victim, criminal):
        # Add criminal to victim's memory
        #FIXME getting 'AttributeError: 'Criminal' object has no attribute 'add_to_memory'
        #FIXME every time this is called.
        
        #victim.add_to_memory(criminal)

        # Probability of success - replace with any equation, e.g. including crime propensity
        criminal.increase_propensity()
        print(str(criminal) + " successfully robbed " + str(victim) + " at %s." % str(victim.pos))

        if criminal.network:
            # Distribute resources across coalition
            split = (victim.resources[0]/2)/len(criminal.network.members)

            for member in criminal.network.members:
                member.resources[0] += split
        else:
            # Criminal get's 100% of the stolen goods
            criminal.resources[0] += victim.resources[0]/2

        # Victim loses money
        victim.resources[0] /= 2

    @crime_wrapper
    def attempt_nonviolent_crime(self, criminal, victim):

        if isinstance(victim, Building) or isinstance(victim, CommercialBuilding):
            self.decrement_building_attractiveness(victim, 1)
            print(str(criminal) + " successfully robbed " + str(victim) + " at %s." % str(victim.pos))


            neighbor_buildings = list(
                filter(
                    lambda x: isinstance(x, Building),
                    self.grid.get_neighbors(victim.pos, moore=True, include_center=False, radius=1)))

            for building in neighbor_buildings:
                self.decrement_building_attractiveness(building, 0.5)


            # Give Criminal resources for crime
            criminal.resources[0] += 5



    def _imprison_criminal(self, criminal, police):
        """Actually arrest a criminal: Take them to the station"""
        # Take the criminal's resources
        # FIXME who gets resources? Return them? Officer? Police Department? Is that a tuneable policy?
        self._seize_assets(criminal, police)

        # Incarcerate criminal
        self.grid.move_agent(criminal, self.pd.pos)
        criminal.is_incarcerated = True
        criminal.remaining_sentence = random.randint(1, self.config['maximum_sentence'])

        # Free up officer by retracting dispatch order
        police.drop_investigation()  # drop the dispatch coordinates



    def _remove_criminal(self, criminal, police):
        """Remove a criminal from the simulation."""
        # Take the criminal's resources
        # FIXME who gets resources? Return them? Officer? Police Department? Is that a tuneable policy?
        self._seize_assets(criminal, police)

        # Remove the criminal from the simulation
        if criminal.network is not None:  # Remove from coalition
            criminal.leave_coalition()
        self.schedule.remove(criminal)  # Remove from scheduler

        if criminal in self.agents['criminals']:
            self.agents['criminals'].remove(criminal)  # Remove from environment
            del criminal  # Remove from memory

        # Free up officer by retracting dispatch order
        police.drop_investigation()  # drop the dispatch coordinates

    def _seize_assets(self, criminal, police):
        """Defines what happens with a criminal's resources when they are arrested"""
        police.resources[0] += criminal.resources[0]
        criminal.resources[0] = 0
        return

    def call_police(self, victim, agent):
        """Call the police, give them a description of the criminal.

        params:
            agent (Criminal): The criminal that the police should look out for
        """
        self.pd.dispatch(victim, agent)

    def has_sufficient_propensity(self, agent):
        """Checks if an agent can DO CRIME with current propensity.

        An Agent in a coalition uses their coalition's combined propensity.
        """
        if agent.network is not None:
            # Agent is in coalition, use coalition's combined propensity
            return agent.network.combined_crime_propensity >= self.config['crime_propensity_threshold']
        else:
            # Agent is NOT in a coalition, use their personal propensity
            return agent.crime_propensity >= self.config['crime_propensity_threshold']

    def can_be_solo(self, agent):
        """Returns true if personal propensity exceeds threshold"""
        return agent.crime_propensity >= self.config['crime_propensity_threshold']

    def attempt_join_coalition(self, agent, target_agent):
        """Controls for whether a successful coalition join occurs. Factors we may want to consider: if the coalition \
        wants the agent, respect, etc.

        However, for now will have 100% success

        Returns:
            True if agent successfully joins coalition
        """
        assert(agent.network is None)
        if target_agent.network is None:
            # Create a new network
            coalition = self.new_coalition()
            coalition.add_member(agent)
            coalition.add_member(target_agent)
        else:
            # Join their coalition
            target_agent.coalition.add_member(agent)
        return True

    def attempt_merge_coalition(self, target_coalition, other_coalition):
        """Merge other coalition into target coalition, and remove the other coalition from existence.

        Currently works 100% of the time.
        """
        # Todo implement - currently done in Criminal
        return

    def new_coalition(self):
        """Creates and returns a brand new coalition with a unique id."""
        uid = copy.deepcopy(self.next_coalition_uid)
        self.next_coalition_uid += 1

        self.criminal_coalitions.append(
            Coalition_Crime(uid, self))

        self.total_coalitions += 1

        logging.info("Added new coalition: {0}".format(str(self.criminal_coalitions[-1])))
        for coalition in self.criminal_coalitions:
            logging.info(str(coalition))
        return self.criminal_coalitions[-1]

    def remove_coalition(self, coalition):
        """Removes a coalition from the environment."""
        if coalition in self.criminal_coalitions:
            self.criminal_coalitions.remove(coalition)
            self.total_coalitions -= 1

    # Building Functions
    def improve_building_attractiveness(self, building):
        """Improve a building's attractiveness with the specified function.

        TODO For now, just an asymptotic function of time
        """

        building.attractiveness += (1 - building.attractiveness) * 0.01

    def decrement_building_attractiveness(self, building, magnitude):
        """Decrease a building's attractiveness

        Proportionally decreases by 2^magnitude, so at most half

        Params:
            magnitude (float): A number 0-1, 1 is maximum decrementitude
        """

        building.attractiveness /= 2**magnitude

    def next_building_id(self):
        """Gets and updates the next building id"""
        self.next_building_id += 1
        return self.next_building_id - 1

    def can_agent_occupy_cell(self, cell):
        """Helper function, returns True if cell does not have a building object in it. """
        contents = self.grid.get_cell_list_contents(cell)

        for agent in contents:
            if type(agent) in [Building, CommercialBuilding]:
                return False

        # No agents were buildings, agent can walk there
        return True
    

class Decorators(object):
    """Contains decorator functions to control functions inside the environment."""
    def __init__(self):
        self.config = cfg.environ

    @classmethod
    def crime_wrapper(cls, crime_function):
        """Controls for how a criminal commits a crime."""

        @functools.wraps(crime_function)
        def inner_wrapper(self, *args, **kwargs):
            logging.info("Got this far")
            p = self.config['crime_success_probability']
            if random.random() < p:
                logging.info("Crime Successful")
                self.total_crimes += 1
                crime_function(self, *args, **kwargs)
            else:
                logging.info("Crime not Successful")
        return inner_wrapper

        


