import config.environ_config as cfg
import numpy as np
import random
import Coalition_Crime
import Agent
import matplotlib.pyplot as plt
import copy

class Environment(object):
    '''
    An environment inside the world, describes a space and the rules for interaction
    between agents and resources. Can be spatial (grid-like) or non-spatial (nodes and connections).
    '''

    def __init__(self, eid, spatial=True):
        '''
        Constructor
        :param: agents List <agents>: A list of agents in this environment
        '''

        # Unique Environment ID
        self.eid = eid

        # Load Environment config
        self.config = cfg.environ

        # History of resources
        # FIXME implement correctly
        self.resourceHistory = []

        # List of agents
        self.coalitions = list()
        self.civilians = list()
        self.police = list()

        if spatial:
            self.__genetate_grid()


    def tick(self):
        # commit a crime
        new_place = []

        for g in self.criminals:
            if g.commit_crime(self.civilians, self.police, self.config['crime_propensity_threshold']):
                new_place.append([g.location[0], g.location[1]])
                print("Crime happens at" + str(new_place) + ".")

        if len(new_place) != 0:
            self.crime_place = new_place

        # police move
        random.shuffle(self.police)
        for i in range(len(self.police)):
            # move to the crime place immediately
            if i + 1 <= len(self.crime_place):
                self.police[i].move(self.config['grid_width'], self.config['grid_height'], self.crime_place[i])
            else:
                # randomly move
                self.police[i].move(width=self.config['grid_width'], height=self.config['grid_height'])

        # coalitionss split
        # FIXME copying probably not necessary
        copy_coalitions = copy.deepcopy(self.coalitions)
        self.coalitions = []
        for i in range(len(copy_coalitions)):
            k = 0
            for j in range(len(copy_coalitions[i].members)):
                c = copy_coalitions[i].members[k]
                if c.crime_propensity >= self.config['crime_propensity_threshold']:
                    copy_coalitions[i].members.remove(c)
                    self.coalitions.append(Coalition_Crime([c], copy_coalitions[i].location[0], copy_coalitions[i].location[1]))
                    continue
                k = k + 1
            if len(copy_coalitions[i].member) != 0:
                self.coalitions.append(Coalition_Crime(members=copy_coalitions[i].members,
                                                       location=[copy_coalitions[i].location[0],
                                                       copy_coalitions[i].location[1]]))

        # coalitionss move
        for g in self.coalitions:
            g.move_together(self.config['grid_width'], self.config['grid_height'])

        # coalitionss form
        copy_coalitions = copy.deepcopy(self.coalitions)
        self.coalitions = []
        for i in range(self.config['grid_width']):
            for j in range(self.config['grid_height']):
                a = []
                # coalitionss whose propensity are less than the threshold form a big coalitions
                for g in copy_coalitions:
                    if g.x >= i and g.x < i + 1 and g.y >= j and g.y < j + 1 and g.tot_prop < self.config['crime_propensity_threshold']:
                        a = a + g.member
                    if g.x >= i and g.x < i + 1 and g.y >= j and g.y < j + 1 and g.tot_prop >= self.config['crime_propensity_threshold']:
                        self.coalitions.append(Coalition_Crime(member=g.members, location=[g.location[0], g.location[1]]))
                if len(a) > 0:
                    self.coalitions.append(Coalition_Crime(member=a, location=[i + 0.5, j + 0.5]))

        # civilians move
        for c in self.civilian:
            c.move(self.config['grid_width'], self.config['grid_height'])
        pass

    def get_expected_resource(self):
        # FIXME implement
        return 0

    def __genetate_grid(self):
        # FIXME generate grid
        self.grid_width = self.config['grid_width']
        self.grid_height = self.config['grid_height']
        pass

    def populate(self):
        '''
        Initiate random population placement onto spatial grid
        :param agents: List of agents in simulation
        :return:
        '''

        # To keep track of coalitions


        # Criminals are in their own coalition at first
        for coalition_id in range(self.config['num_criminals']):
            # Create a coalition
            new_coalition = Coalition_Crime(uid=coalition_id)
            new_agent = Agent(of_type=0, uid=coalition_id, network=new_coalition,
                              crime_propensity=random.uniform(0,self.config['crime_propensity_init_max']),
                              location=[random.uniform(0,self.config['grid_width']), random.uniform(0, self.config['grid_height'])],
                              resources=random.uniform(0, self.config['resouces_init_max_for_criminals']))
            self.coalitions.append(new_coalition)



        # Populate Civilians
        for civilian_id in range(self.config['num_criminals'], self.config['num_civilians']):
            self.civilians.append(
                Agent(of_type=1, uid=civilian_id,
                      location= list(random.uniform(0, self.config['grid_width']), random.uniform(0, self.config['grid_height'])),
                      resources = list(random.uniform(0, self.config['resources_init_max_for_civilians'])))
            )


        for police_id in range(len(self.coalitions) + len(self.civilians), self.config['num_police']):
            self.police.append(
                Agent(of_type=2, uid=police_id,
                      location=[random.uniform(0, self.config['grid_width']),
                                random.uniform(0, self.config['grid_height'])])
            )



    def update_grid(self):
        # Plot agents onto grid
        ax = plt.subplot()
        ax.xaxis.set_major_locator(plt.MultipleLocator(1))
        ax.xaxis.grid(True, which='major')
        ax.yaxis.set_major_locator(plt.MultipleLocator(1))
        ax.yaxis.grid(True, which='major')

        a = {0: "brown", 1: "olive", 2: "darkgray", 3: "darkgreen", 4: "darkorange", 5: "yellow", 6: "darkviolet",
             7: "firebrick", 8: "pink", 9: "gold", 10: "lightblue"}


        for coalition in self.coalitions:
            for criminal in coalition.members:
                ax.scatter(criminal.location[0], criminal.location[1], color=a[8], marker='x')

        for civilian in self.civilians:
            ax.scatter(civilian.location[0], civilian.location[1], color="blue")

        for police in self.police:
            ax.scatter(police.location[0], police.location[1], color="black", marker='o')

        ax.set_xlim(0, self.config['grid_width'])
        ax.set_ylim(0, self.config['grid_height'])

        plt.show()
