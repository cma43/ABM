import config.environ_config as cfg
import numpy as np
import random
from Coalition_Crime import Coalition_Crime
from agent_cma_zl import Agent
import matplotlib.pyplot as plt
import copy
from collections import namedtuple

class Environment(object):
    '''
    An environment inside the world, describes a space and the rules for interaction
    between agents and resources. Can be spatial (grid-like) or non-spatial (nodes and connections).
    '''

    def __init__(self, uid, spatial=True):
        '''
        Constructor
        :param: agents List <agents>: A list of agents in this environment
        '''

        # Unique Environment ID
        self.uid = uid

        # Load Environment config
        self.config = cfg.environ

        # History of resources
        # FIXME implement correctly
        self.resourceHistory = []

        # List of agents
        self.agents = list()
        self.coalitions = list()

        self.civilians = list()
        self.police = list()
        self.criminals = list()
        
        self.crime_place = []
        # self.crime_place.append((0,0))
        if spatial:
            self.__generate_grid()

        self.crimes_this_turn = list()


    def tick(self):

        self.crimes_this_turn = list()

        # FIXME Took this out for now - was causing issues - also the global lists for agents and roles are already made in populate()
        total_agent_list = []

        #for agent in Agent.getInstances():
         #  total_agent_list.append(agent)
         #  if agent.Role.CIVILIAN:
        #       self.civilians.append(agent)
        #   if agent.Role.POLICE:
        #       self.police.append(agent)
           #if agent is in a crime coalition, append coalition list here

        # commit a crime
        new_place = []
        for g in self.coalitions:
            crime = g.commit_crime(civilians=self.civilians,
                              police=self.police,
                              threshold=self.config['crime_propensity_threshold'], 
                              vision_radius=self.config['agent_vision_limit'],
                              crime_radius=self.config['crime_distance'])
            if crime:
                new_place.append([crime[0], crime[1]])
                print("Coalition " + str(g.uid) + " robs someone at " + str(new_place[-1]) + ".")

        self.crimes_this_turn = new_place
        self.crime_place += new_place

        # police move
        random.shuffle(self.police)
        for i in range(len(self.police)):
            # move to the crime place immediately
            if len(self.crime_place) > 0:
                self.police[i].move(self.config['grid_width'], self.config['grid_height'], self.crime_place[0][0], self.crime_place[0][1])
                self.crime_place.remove(self.crime_place[0])
            else:
                # randomly move
                self.police[i].move(width=self.config['grid_width'], height=self.config['grid_height'])

        # coalitions split
        # FIXME Not very readable
        random.shuffle(self.coalitions)
        for coalition in self.coalitions:
            if len(coalition.members) > 1:
                for criminal in coalition.members:
                   if criminal.crime_propensity > self.config['crime_propensity_threshold'] and len(coalition.members) > 1:
                       # Split and make new coalition
                       coalition.members.remove(criminal)
                       max_coalition_id = self.config['num_criminals'] + 1
                       for coalition in self.coalitions:
                           if coalition.uid >= max_coalition_id:
                               max_coalition_id = coalition.uid + 1
                       new_coalition = Coalition_Crime(uid=max_coalition_id,
                                                       members=[criminal],
                                                       combined_crime_propensity=criminal.crime_propensity,
                                                       x=criminal.x,
                                                       y=criminal.y)
                       self.coalitions.append(new_coalition)
                       criminal.network = new_coalition
                       print("Criminal %s split from Coalition %s to form new Coalition %s" % (str(criminal.uid), str(coalition.uid) ,str(new_coalition.uid) ))


        # coalitionss move
        for g in self.coalitions:
            g.move_together(self.config['grid_width'], self.config['grid_height'])


        # coalitionss form

        # FIXME Using new Coalition.Merge_Coalitions - Currently first coalition will absorb second, order randomized.
        random.shuffle(self.coalitions)
        for coalition in self.coalitions:
            for other_coalition in self.coalitions:
                if coalition.uid != other_coalition.uid and \
                        coalition.distance(other_coalition) <= 1 and \
                        (coalition.merge_with_coalition(other_coalition, self.config['crime_propensity_threshold'])):
                    print("Coalition " + str(coalition.uid) + " merged with another coalition and now has " + str(len(coalition.members)) + " members")
                    self.coalitions.remove(other_coalition)

        # civilians move
        for c in self.civilians:
            c.move(self.config['grid_width'], self.config['grid_height'])

    def get_expected_resource(self):
        # FIXME implement
        return 0

    def __generate_grid(self):
        # FIXME generate grid
        self.grid_width = self.config['grid_width']
        self.grid_height = self.config['grid_height']
        pass

    def populate(self):
        '''
        Initiate random population placement onto spatial grid
        Populates global list of all agents, all criminals, all civilians, all police, each with their own list
        :return:
        '''

        # To keep track of coalitions

        
        # Criminals are in their own coalition at first
        for coalition_id in range(self.config['num_criminals']):
            # Create a coalition
            new_coalition = copy.deepcopy(Coalition_Crime(uid=coalition_id))
            new_agent = Agent(of_type=Agent.Role.CRIMINAL, uid=coalition_id, network=new_coalition,
                              crime_propensity=random.uniform(0,self.config['crime_propensity_init_max']),
                              x=round(random.uniform(0,self.config['grid_width'])),
                              y=round(random.uniform(0, self.config['grid_height'])),
                              resources=[random.uniform(0, self.config['resources_init_max_for_criminal'])])
            self.agents.append(new_agent)
            self.criminals.append(new_agent)
            new_coalition.members.append(new_agent)
            new_coalition.x, new_coalition.y = new_agent.x, new_agent.y
            self.coalitions.append(new_coalition)

        # Populate Civilians
        for civilian_id in range(0, self.config['num_civilians']):

            self.civilians.append(
                Agent(of_type=Agent.Role.CIVILIAN,
                      uid=civilian_id,
                      x=round(random.uniform(0, self.config['grid_width'])),
                      y=round(random.uniform(0, self.config['grid_height'])),
                      resources=list(random.sample(range(0, self.config['resources_init_max_for_civilian']),1)))
            )

        # Populate Police
        for police_id in range(self.config['num_criminals'] + self.config['num_civilians'], self.config['num_criminals'] + self.config['num_civilians'] +self.config['num_police']):
            self.police.append(
                Agent(of_type=Agent.Role.POLICE, uid=police_id,
                      x=round(random.uniform(0, self.config['grid_width'])),
                      y=round(random.uniform(0, self.config['grid_height'])))
            )

        #self.update_grid(title="Initial State")


    def update_grid(self, title="Title"):
        # Plot agents onto grid
        plt.title(str(title))
        ax = plt.subplot()
        ax.xaxis.set_major_locator(plt.MultipleLocator(1))
        ax.xaxis.grid(True, which='major')
        ax.yaxis.set_major_locator(plt.MultipleLocator(1))
        ax.yaxis.grid(True, which='major')

        a = {0: "brown", 1: "olive", 2: "darkgray", 3: "darkgreen", 4: "darkorange", 5: "yellow", 6: "darkviolet",
             7: "firebrick", 8: "pink", 9: "gold", 10: "lightblue"}

        for coalition in self.coalitions:
            #print("COALITION: " + str(coalition.uid) + " " + str(coalition.x) + ", " + str(coalition.y))
            ax.annotate(str(coalition.uid), (coalition.x, coalition.y))
            for criminal in coalition.members:
                #print(str(criminal.uid) + ": " + str(criminal.x) + ", " + str(criminal.y))
                ax.scatter(criminal.x, criminal.y, color="red", marker='x')


        for civilian in self.civilians:
            ax.scatter(civilian.x, civilian.y, color="blue")

        for police in self.police:
            ax.scatter(police.x, police.y, color="black", marker='o')

        ax.set_xlim(0, self.config['grid_width'])
        ax.set_ylim(0, self.config['grid_height'])

        plt.show()
