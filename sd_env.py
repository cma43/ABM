from mesa import Model
#from time_test import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
from Agent.sd_agent import SDAgent
import numpy as np 
import random as random

C=1
D=0

class SDGrid(Model):
    ''' Model class for iterated, spatial social dilemma model. '''

    schedule_types = {"Sequential": BaseScheduler,
                      "Random": RandomActivation,
                      "Simultaneous": SimultaneousActivation}

    # This dictionary holds the payoff for this agent,
    # keyed on: (my_move, other_move)

    #NOTE: Payoffs must be given by the user in the format below as a dict object. 
    
    def __init__(self, height=0, width=0, schedule_type="Random", payoffs=None, seed=2514, p = .1, implement = "Epstein", num_RL =500, ep_length=1):
        '''
        Create a new Spatial Prisoners' Dilemma Model.
        Args:
            height, width: Grid size. There will be one agent per grid cell.
            schedule_type: Can be "Sequential", "Random", or "Simultaneous".
                           Determines the agent activation regime.
            payoffs: (required) Dictionary of (move, neighbor_move) payoffs.
        '''
        #Set default grid size if none inputted by user
        if height == 0:
            h = 50
        else:
            h = height
        if width == 0:
            w = 50
        else:
            w = width
        
        assert height or width < 0, "Grid heigth and width must be positive numbers."

        if payoffs:
            self.payoff = payoffs
        
        else: 
            self.payoff = {(C, C): 5,
                        (C, D): -5,
                        (D, C): 6,
                        (D, D): -6}

        self.grid = SingleGrid(h, w, torus=True)
        self.schedule_type = schedule_type
        self.schedule = self.schedule_types[self.schedule_type](self)
        self.implement = implement
        self.ep_length = ep_length
        self.num_RL = num_RL
        #FIXME: THis is a bandaid fix for MESA's loop bug (see trello for SD ABM):

        self.kill_list = []
        self.fertile_agents = []

        if self.implement == "Epstein":
            leave_empty = np.random.choice(a = [False, True], size = (width, height), p = [p, 1-p])
        else:
            pass

        # Create agents: automatically populates agents and grid; 
        count = 0
        for x in range(width):
            for y in range(height):
                
                if implement == "Epstein":
                    if leave_empty[x, y]:
                        continue
                    else:
                        agent = SDAgent(count, (x, y), self)
                        count +=1
                else:
                    agent = SDAgent(count, (x, y), self)
                    count +=1

                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
########################################################################################################################
        #FIXME: may need to make an unique id for agents to do this correctly
        #FIXME: this will have to be generalized later for when multipe batches of episodes are being run
########################################################################################################################
        # learners = np.random.choice([self.schedule._agents], self.num_RL) 

        # #switch them to learn mode
        # for agent in learners:
        #     agent.learn_mode = True
        

        # TODO: Make data collection easier for user; need to do same in BWT / Cartel

        self.datacollector = DataCollector(model_reporters={
            "Learning Cooperating_Agents":
            lambda m: (len([a for a in m.schedule.agents if a.move == C and a.unique_id == 1] )),
            "Learning Defecting_Agents": 
            lambda n: (len([b for b in n.schedule.agents if b.move == D and b.unique_id == 1] ))
        })

        self.running = True
        self.datacollector.collect(self)

    def step(self):

        self.schedule.step()
        for agent in self.schedule.agents:
            if agent.unique_id == 1:
                agent.learn = True
                #print('agent 1 has learn set to {}'.format(agent.learn))
                agent.update_policy()
        # collect data
        self.datacollector.collect(self)

        # self.purge()
        # self.replicate_agents()

        #if (self.schedule.time % self.ep_length == 0) and (self.schedule.time > 0):
            #print(self.schedule.time)
            
            # learners = random.sample(self.schedule.agents, self.num_RL) 
            # for agent in learners:
            #     agent.learn = True
        
            # for agent in learners:
            #     agent.update_policy()
            #     agent.learn = False
            #     if agent == learners[-1]: 
            #         print("################################# Update finished #################################")
            

        
    def replicate_agents(self):
        
        if self.fertile_agents is not None:

            for agent in self.fertile_agents:
                if agent.pos is not None:
                    try:
                        agent.replicate()
                    except ValueError:
                        #print("Caught a bad egg, boss!")
                        continue


    def purge(self):

        if len(self.kill_list)>0:
            for agent in self.kill_list:
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
        
            self.kill_list = []
        else:
            pass


    def run(self, n):
        ''' Run the model for n steps. '''
        for _ in range(n):
            self.step()