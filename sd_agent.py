from mesa import Agent
import random as random
import numpy as np 
import torch as torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable
from torch.distributions import Categorical

LEARN_RATE = .01
GAMMA = .99999
DROPOUT = .6
C = 1
D = 0

############################################
#TODO: Check action selection is updating and selecting properly; currently C and D is .5 throughout the entire simulation and can't be correct
############################################
#TODO: would be nice to have functions in OABM that give easy-to-plug-and-play NNs as an option for agents (and to customize in a basic way)

class Policy(nn.Module):

    def __init__(self, input_dim, output_dim):
        super(Policy, self).__init__()

        self.input_dim = input_dim
        self.output_dim = output_dim

        self.l1 = nn.Linear(self.input_dim, 10, bias=False)
        self.l2 = nn.Linear(10, self.output_dim, bias = False)

        self.gamma = GAMMA
        self.learning_rate = LEARN_RATE

        #Episode policy and reward history
        self.policy_history = torch.Tensor()
        self.reward_episode = []

        #TODO: allow these histories to be parameterized by agent memory 'm'
        #Overall reward and loss history 
        self.reward_hist = []
        self.loss_hist = []

    def forward(self, x):

        model = nn.Sequential(self.l1,
                                    nn.ReLU(), self.l2, nn.Softmax(dim = -1)
        )

        return model(x)


###################################################################################

class SDAgent(Agent):
    ''' Agent member of the iterated, spatial prisoner's dilemma model. '''

    def __init__(self, unique_id, pos, model, starting_move=None, threshold = 10, q = .5, age_lim = False, mutate = False, RL = True, freq = 10):
        '''
        Create a new Social Dilemma agent. Relies on payoff structure from model.
        Assume's Epstein's version of evolutionary PD. 

        Args:
            pos: (x, y) tuple of the agent's position.
            model: model instance
            starting_move: If provided, determines the agent's initial state:
                           C(ooperating) or D(efecting). Otherwise, random.
            threshold: cutoff for replicating
            q: probability of choosing C or D as starting move
            age_lim: boolean; if True, enforce an agent limit to agents
            mutate: randomly assign agent type after an agent replicates if true
            RL: give the agent the ability to learn using reinforcement learning (RL) 
        '''
        super().__init__(pos, model)
        self.unique_id = unique_id
        self.pos = pos
        self.score = 0
        self.G = [] #The sum of returns, using sutton and barto's notation
        self.score_list = []
        self.age = 1
        self.RL = RL #This indicates that the agent is an RL agent; if learn is true, then the agent also can update its policy 
        self.next_move = None
        self.threshold = threshold
        self.vision = 1 #Describes vision radius for agent 
        self.endowment_to_give = 6
        self.age_lim = age_lim
        if self.age_lim:
            self.max_age = 100
        self.mutate = mutate
        if starting_move:
            self.move = starting_move
        # if self.mutate:
        #     self.move = np.random.choice([C,D], p = [q,1-q])
        else:
            self.move = np.random.choice([C, D], p = [q, 1-q])

        #Create instances of policy network and optimizer, with state and action space dimensions

        self.state_dim = 2 #Assuming can observe number of C and number of D agents
        self.action_dim = 2 #Only have actions C and D
        self.policy = Policy(self.state_dim, self.action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr = LEARN_RATE)
        self.m = 20 #The agent's memory parameter
        self._learn = False
        self.update_frequency = freq

    @property
    def isCooperating(self):
        return self.move == C
    
    @property
    def learn(self):
        #print("Getting learn value")
        return self._learn 

    @learn.setter
    def learn(self, learn_bool):
        #print("Learn value changed from {} to {}".format(self._learn, learn_bool))
        self._learn = learn_bool
        #print("Learn value is now {}".format(self._learn))


    def select_action(self, state):
    #Select an action (0 or 1) by running policy model 
    # and choosing based on the probabilities in state 
    
        state = torch.from_numpy(state).type(torch.FloatTensor)
        state = self.policy(state)
        c = Categorical(state)
        
        _, max_index = state.max(0)
        action = max_index

        #action = c.sample()
        

        # Add log probability of our chosen action to our history    
        self.update_policy_hist(c.log_prob(action))
            
        return action

    def update_policy_hist(self, action):

        if self.policy.policy_history.dim() == 0:
            self.policy.policy_history = action
            # print('Policy history updated')
            # print(self.policy.policy_history)
        else:
            # print(type(self.policy.policy_history))
            # print(type(action))
            if not isinstance(action, int):
                self.policy.policy_history = torch.cat([self.policy.policy_history, torch.FloatTensor(action.reshape(1))])
            else:
                self.policy.policy_history = torch.cat([self.policy.policy_history, torch.FloatTensor(action)])
            # print('Policy history updated')
            # print(self.policy.policy_history)

        return 


    def update_policy(self):

        #Updates policy based on memory paramter self.m using REINFORCE 

        R = 0
        #policy_los
        T = len(self.policy.reward_episode)-1
        memory = T - self.m

        #TODO: Try sampling random chunks of size memory
        
        # Discount future rewards back to the present using gamma
        for r in self.policy.reward_episode[T:memory:-1]:
            R = r + self.policy.gamma * R
            self.G.insert(0,R)
            
            
        # Scale rewards
        rewards = torch.tensor(self.G)
        rewards = (rewards - rewards.mean()) / (rewards.std() + np.finfo(np.float32).eps)
        
        #TODO: Try out using replay buffer rather than serial memory for updating NN

        policy_hist = self.policy.policy_history.flatten().tolist()

        policy_hist = torch.FloatTensor(policy_hist[T:memory:-1])

        #print(policy_hist)
        loss = (torch.sum(torch.mul(policy_hist, rewards).mul(-1), -1))
        loss = Variable(loss, requires_grad = True)
        #print(loss)
        # Update network weights
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        #Save and intialize episode history counters
        #self.policy.loss_hist.append(loss.item())
        #self.policy.reward_hist.append(np.sum(self.policy.reward_episode))
        #self.policy.policy_history = Variable(torch.Tensor())
        #self.policy.reward_episode= []

        self.G = []
        #print ('agent {} has updated their policy'.format(self.unique_id))
        return 


    def step(self):
        ''' Get the neighbors' moves, and change own move accordingly. '''

        if self.model.implement != "Epstein":
            neighbors = self.model.grid.get_neighbors(self.pos, False,
                                                    include_center=True, radius = self.vision)
            best_neighbor = max(neighbors, key=lambda a: a.score)
            self.next_move = best_neighbor.move

            if self.model.schedule_type != "Simultaneous":
                self.advance()
        
        
        else: 
           
            #choose unoccupied spot, go there. play each neighbor. update score. 
            #if score above threshold, then replicate. if score
            #below 0, then die. 

            immediate_nbd = self.model.grid.iter_neighborhood(self.pos, False, include_center=True, radius = self.vision)
            cells_in_range = [cell for cell in immediate_nbd if self.model.grid.is_cell_empty(cell)]

            if len(cells_in_range) > 1:
                self.model.grid.move_agent(self, random.choice(list(cells_in_range)))
            if len(cells_in_range) == 1:
                cell = cells_in_range[0]
                self.model.grid.move_agent(self, cell)

            if self.model.schedule_type != "Simultaneous":
                self.advance()
            
            if self.age_lim:
                if self.max_age <= self.age:
                    self.die()

        
    def die(self):
        #self.model.grid.remove_agent(self)
        #self.model.schedule.remove(self)
        self.model.kill_list.append(self)
        
        return 

    def replicate(self):

        if self.score <= self.threshold:
            raise ValueError("Score is not high enough to replicate!")

        #If an open space in the grid beside the agen, replicate
        immediate_nbd = self.model.grid.iter_neighborhood(self.pos, False, include_center=False, radius = self.vision)
        if immediate_nbd is not None:
            cells_in_range = [cell for cell in immediate_nbd if self.model.grid.is_cell_empty(cell)]
        
        if self.mutate:
            strategy = random.choice([C,D])
        else:
            strategy = self.move
                       
        if cells_in_range is not None and len(cells_in_range) == 1:
            agent = SDAgent(cells_in_range[0], self.model, strategy)
            agent.score += self.endowment_to_give
            self.score -= self.endowment_to_give
            self.model.grid.place_agent(agent, agent.pos)
            self.model.schedule.add(agent)

        if cells_in_range is not None and len(cells_in_range) > 1:
            agent = SDAgent(random.choice(cells_in_range), self.model, strategy) 
            agent.score += self.endowment_to_give
            self.score -= self.endowment_to_give
            self.model.grid.place_agent(agent, agent.pos)
            self.model.schedule.add(agent)
            
        return 

    def advance(self):

        if self.model.implement != "Epstein":
            self.move = self.next_move
            self.score += self.increment_score()

        else:

            if self.RL:
                # print('agent {} turnin up to learn up'.format(self.unique_id))
                #FIXME: this assumes the agent updates and tracks itself; the env
                #should be doing this. O/w the agent acts as if its policy is fixed in
                #its action selection.   

                # if self.model.schedule.time % self.model.ep_length and self.learn == True:
                #     self.update_policy()
                self.score += self.increment_score()
                # print('agent {} updated'.format(self.unique_id))
                # print('agent {} has learn set to {}'.format(self.unique_id, self.learn))
                
                if self.learn:
                    #print('turm tur lurm')
                    immediate_nbd = self.model.grid.get_neighbors(self.pos, False, include_center=False, radius = self.vision)
                    num_coop = len([agent for agent in immediate_nbd if agent.move == C])
                    num_def = len([agent for agent in immediate_nbd if agent.move == D])
                    self.move = self.select_action(np.array([num_coop, num_def]))
                else:
                    self.update_policy_hist(self.move)
                
            else:
                self.score += self.increment_score()

                if self.score < 0:
                    #self.die() #remove from map and memory
                    self.model.kill_list.append(self)
                if self.score > self.threshold:
                    self.replicate()
                    self.model.fertile_agents.append(self) 
                
                if self.age_lim:
                    self.age += 1
 

    def increment_score(self):
        
        neighbors = self.model.grid.get_neighbors(self.pos, True)
        
        if self.model.implement != "Epstein":


            if self.model.schedule_type == "Simultaneous":
                moves = [neighbor.next_move for neighbor in neighbors]
            else: 
                moves = [neighbor.move for neighbor in neighbors]
            return sum(self.model.payoff[(self.move, move)] for move in moves)
       
        else:
            
        
            if self.model.schedule_type == "Simultaneous":
                moves = [neighbor.next_move for neighbor in neighbors]
                if self.RL:
                    new_moves = []

                    if self.move != 0 or self.move !=1:
                        self.move = self.move.item()
                    for move in moves:
                        if move != 0 or move != 1:
                            new_moves.append(move.item())
                        else:
                            new_moves.append(move)

                    reward = sum(self.model.payoff[(self.move, move)] for move in new_moves)
                    self.policy.reward_episode.append(reward)

            else: 
                moves = [neighbor.move for neighbor in neighbors]
                if self.RL:
                    new_moves = []
                    
                    if self.move == torch.tensor(0) or self.move == torch.tensor(1):
                        #print(self.move)
                        if not isinstance(self.move, int):
                            self.move = self.move.item()
                        
                    
                    for move in moves:
                        if move == torch.tensor(0) or move == torch.tensor(1):
                            #print(move)
                            if not isinstance(move, int):
                                new_moves.append(move.item())
                            else:
                                new_moves.append(move)
                        else:
                            new_moves.append(move)


                    reward = sum(self.model.payoff[(self.move, move)] for move in new_moves)
                    self.policy.reward_episode.append(reward)

                    #FIXME: How are we collecting data and associating it with inputs? We want to exclude sparse data

            return reward

    
            