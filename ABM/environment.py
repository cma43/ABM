import config.environ_config as cfg
import random
import matplotlib.pyplot as plt
from mesa import space
from mesa import time
from mesa.datacollection import DataCollector

from RAT_example.Police_Department import PoliceDepartment
from RAT_example.rat_agents import Police, Criminal, Civilian
from RAT_example.Coalition_Crime import Coalition_Crime
import numpy as np
import copy

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

        # Initial population parameters
        self.population_counts = {
            'civilians': self.config['num_civilians'],
            'criminals': self.config['num_criminals'],
            'police':  self.config['num_police']
        }

        # Grid from mesa
        self.grid = space.MultiGrid(width=self.config['grid_width'],
                                    height=self.config['grid_height'],
                                    torus=False)

        # Scheduler from Mesa
        self.scheduler = time.RandomActivation(self)

        self.agents = {
            'civilians' : list(),
            'criminals' : list(),
            'police' : list()
        }
        self.next_criminal_uid = len(self.agents['criminals'])

        self.criminal_coalitions = list()
        self.next_coalition_uid = 0

        # FIXME To be implemented
        # History of resources
        self.resourceHistory = []

    def tick(self):
        """One step of the simulation"""
        self.pre_step()
        self.scheduler.step()

    def run(self, num_steps):
        """Run one batch for the desired number of steps"""
        self.populate()

        for step in range(num_steps):
            self.tick()
            self.plot()

    def plot(self):
        """Draw the environment and the agents within it."""
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.grid.width)
        ax.set_ylim(0, self.grid.height)
        ax.scatter([agent.pos[0] for agent in self.agents['civilians']],
                   [agent.pos[1] for agent in self.agents['civilians']],
                   color="green",
                   alpha=0.5)
        ax.scatter([agent.pos[0] for agent in self.agents['criminals']],
                   [agent.pos[1] for agent in self.agents['criminals']],
                   color="red",
                   alpha=0.5)
        ax.scatter([agent.pos[0] if agent.dispatch_coordinates is not None else None for agent in self.agents['police']],
                   [agent.pos[1] if agent.dispatch_coordinates is not None else None for agent in self.agents['police']],
                   color="blue",
                   alpha=0.95)
        ax.scatter([agent.pos[0] if agent.dispatch_coordinates is None else None for agent in self.agents['police']],
                   [agent.pos[1] if agent.dispatch_coordinates is None else None for agent in self.agents['police']],
                   color="blue",
                   alpha=0.2)
        ax.scatter(self.pd.pos[0], self.pd.pos[1],
                   color="black",
                   marker="+")
        #ax.scatter([agent.pos[0] for agent in self.scheduler.agents], [agent.pos[1] for agent in self.scheduler.agents])
        plt.show()



        # FIXME add data collection

    def pre_step(self):
        """Do any necessary actions before letting agents move"""

        # Create a random number of criminals and dump them on the map
        if not self.config['arrest_behavior'] == "remove":
            # No pre_step necessary
            return

        # Drop a random number of criminals on the map
        num = np.random.poisson(self.config['lambda'])
        for i in range(num):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            new_agent = Criminal(uid=self.next_criminal_uid,
                                 model=self,
                                 pos=(x,y),
                                 resources=[random.randrange(self.config['initial_resource_max'])],
                                 crime_propensity=random.randrange(self.config['initial_crime_propensity_max']))
            self.grid.place_agent(pos=new_agent.pos, agent=new_agent)
            self.agents['criminals'].append(new_agent)
            self.scheduler.add(new_agent)
            print("Criminal " + str(new_agent.uid) + " enters the grid.")
            self.next_coalition_uid += 1

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
        self.pd = PoliceDepartment(uid=1, environment=self)

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
            print(str(criminal) + " successfully robbed " + str(victim) + " at %s." % str(victim.pos))

            if criminal.network:
                # Distribute resources across coalition
                split = (victim.resources[0]/2)/len(criminal.network.members)
                print("Members of {0} each get ${1}".format(str(criminal.network), str(split)))

                for member in criminal.network.members:
                    member.resources[0] += split

            else:
                print("They get all the booty.")
                criminal.resources[0] += victim.resources[0]/2
                victim.resources[0] /= 2

            # increase criminal's propensity
            criminal.increase_propensity()
        else:
            print("Crime failed")

    def attempt_arrest(self, criminal, police):
        """Determines if an arrest is successful"""
        p = 0.5
        if random.random() < p:
            print("Boom! Criminal Arrested")
            if self.config['arrest_behavior'] == 'imprison':
                self._imprison_criminal(criminal, police)
            elif self.config['arrest_behavior'] == 'remove':
                self._remove_criminal(criminal, police)
            return True
        else:
            print("Arrest attempt failed!")
            # FIXME Patience timer?

        return False

    def _imprison_criminal_(self, criminal, police):
        """Actually arrest a criminal: Take them to the station"""
        # Take the criminal's resources
        # FIXME who gets resources? Return them? Officer? Police Department? Is that a tuneable policy?
        self._seize_assets(criminal, police)

        # Incarcerate criminal
        self.grid.move_agent(criminal, self.pd.pos)
        criminal.is_incarcerated = True
        criminal.remaining_sentence = self.config['minimum_sentence']

        # Free up officer by retracting dispatch order
        police.drop_investigation()  # drop the dispatch coordinates
        self.grid.move_agent(police, self.pd.pos)  # police goes to the station with criminal

    def _remove_criminal(self, criminal, police):
        """Remove a criminal from the simulation."""
        # Take the criminal's resources
        # FIXME who gets resources? Return them? Officer? Police Department? Is that a tuneable policy?
        self._seize_assets(criminal, police)

        # Remove the criminal from the simulation
        if criminal.network is not None:  # Remove from coalition
            criminal.leave_coalition()
        self.scheduler.remove(criminal)  # Remove from scheduler

        if criminal in self.agents['criminals']:
            self.agents['criminals'].remove(criminal)  # Remove from environment
            del criminal  # Remove from memory

        # Free up officer by retracting dispatch order
        police.drop_investigation()  # drop the dispatch coordinates
        self.grid.move_agent(police, self.pd.pos)  # police goes to the station with criminal

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

        return

    def new_coalition(self):
        """Creates and returns a brand new coalition with a unique id."""
        uid = copy.deepcopy(self.next_coalition_uid)
        self.next_coalition_uid += 1

        self.criminal_coalitions.append(
            Coalition_Crime(uid, self))

        print("Added new coalition: {0}".format(str(self.criminal_coalitions[-1])))
        for coalition in self.criminal_coalitions:
            print(str(coalition))
        return self.criminal_coalitions[-1]

    def remove_coalition(self, coalition):
        """Removes a coalition from the environment."""
        if coalition in self.criminal_coalitions:
            self.criminal_coalitions.remove(coalition)

