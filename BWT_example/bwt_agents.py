from ABM.agent_cma_zl import Agent
import random
from BWT_example import Building
import math
from ABM.behavior import Behavior as b
from scipy.spatial.distance import euclidean


class Criminal(Agent):
    def __init__(self, pos, model, resources, uid, network=None, hierarchy=None, history_self=[],
                 history_others=[], policy=None, allies=[], competitors=[], utility = [], crime_propensity=None,
                 residence=None, kind=1, workplace=None):
        super().__init__(self, pos, model, resources, uid, network, hierarchy, policy)
        self.pos = pos
        self.environment = model
        self.resources = resources
        self.uid = uid
        self.history_self = history_self
        self.history_others = history_others
        self.allies = allies
        self.competitors = competitors
        self.crime_propensity = crime_propensity
        self.vision = random.randint(1, model.config['agent_vision_limit'])
        self.is_incarcerated = False
        self.remaining_sentence = 0
        self.network = network
        self.hierarchy = hierarchy
        self.policy = policy
        self.residence = residence
        self.utility = utility
        self.workplace = workplace
        
        # Attractiveness for each building
        self.building_memory = list()
        
        # Type of crime the criminal commits. 1: damage a building. 2: rob a civilian. 3: commit a violent crime
        self.kind = kind
    
    def __str__(self):
        return "Criminal " + str(self.uid)

    def __repr__(self):
        return str(self)

    def step(self):
        # Complete one time step
        # If criminal is incarcerated, wait out sentence. On last step of sentence, may leave the police department.
        if self.is_incarcerated:
            self.remaining_sentence -= 1
            print("Criminal has %s steps left in prison sentence" % str(self.remaining_sentence))
            if self.remaining_sentence <= 0:
                self.is_incarcerated = False
                print("Criminal is free!")
            else:
                # Another step in prison
                return

        # Check if we need to search for other coalitions or to split
        #self.update_coalition_status()

        # Look for victims if we have enough propensity
        if self.environment.has_sufficient_propensity(self):
            
            possible_victim = self.look_for_victim(radius=self.vision, include_center=True)
            
            
            if possible_victim and not self.check_for_police():
                
                neighbors = self.environment.grid.get_neighbors(self.pos, True,  radius=self.vision, include_center=False)
                calculate_utility = lambda self, agent: b.utility_function(self, agent) - b.cost_function(self, agent)
                
                current_utility = [calculate_utility(self, neighbor) for neighbor in neighbors]
                
                if(max(current_utility) >= 0):
                    victim_index = current_utility.index(max(current_utility))
                    immediate_victim = neighbors[victim_index] 
            
                # There is a potential victim in the same cell, and no police around - try to rob them
                    print("Attempting crime at {0} against {1}.".format(self.pos, immediate_victim))
                
                    if isinstance(immediate_victim, Agent):
                    #neighbors = self.environment.grid.get_neighbors(self.pos, True,  radius=1, include_center=True)
                    #immediate_victim = max(b.computeUtility(neighbors))
                        self.commit_violent_crime(immediate_victim)
                        self.utility.append(immediate_victim.resources[-1])

                    else:
                    #neighbors = self.environment.grid.get_neighbors(self.pos, True,  radius=1, include_center=True)
                    #immediate_victim = max(b.computeUtility(neighbors))
                        self.commit_nonviolent_crime(immediate_victim)
                        self.utility.append(immediate_victim.attractiveness[-1])
                

            else:  # Look further away for victims if there are none in the same cell
                for radius in range(1, self.vision+1):
                    potential_victim = self.look_for_victim(radius=radius, include_center=False)
                    if potential_victim:
                        print("Possible victim at %s" % str(potential_victim.pos))
                        # Found a victim -- if more than one, choose to pursue
                        # utility maximizing victim 
                        
                        neighbors = self.environment.grid.get_neighbors(self.pos, True,  radius=radius, include_center=False)
                        calculate_utility = lambda self, agent: b.utility_function(self, agent) - b.cost_function(self, agent)
                        utility_list = [calculate_utility(self, neighbor) for neighbor in neighbors]
                        
                        next_victim_pos = b.get_victim_location(utility_list, neighbors)
                        
                        #TODO Check that this works right 
                                                   
                        self.walk_to(next_victim_pos)
                        self.utility.append(-b.cost_function(self, next_victim_pos))
                        return 

        # Couldn't find victim, or insufficient propensity
        self.random_move_and_avoid_role(Police)
        
        # add the buildings in the neighbourhood to the criminal's memory
        neighborhood = self.environment.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        
        for cell in neighborhood:
            for agent_building in self.environment.grid.get_cell_list_contents(cell):
                if type(agent_building) is Building:
                    self.add_to_building_memory(agent_building)
        return
    
    def add_to_building_memory(self, building):
        """Add a building to the civilian's momory.
        """
        self.building_memory.append(building)
        self.building_memory = list(set(self.building_memory)) # remove repeats
    
    def commit_nonviolent_crime(self, victim):
        """Commit a crime against an agent or building in the vicinity.

         Victim is either an Agent or a Building
         """
        # FIXME criminals seem to be very stupid
        # Rob half of their resources if model deems the crime successful
        # This call to the model is an attempt to keep the environment in charge of interaction rules
        
        if self.pos == victim.pos:
            self.environment.attempt_nonviolent_crime(self, victim)

    def commit_violent_crime(self, agent):
        self.environment.attempt_violent_crime(self, agent)
        



    def look_for_victim(self, radius, include_center):
        """Look in the neighborhood for a potential victim to rob.

        :return: An agent object
                 False, if no victims in sight
        """
        neighbors = self.environment.grid.get_neighbors(self.pos, True,  radius=radius, include_center=include_center)
        random.shuffle(neighbors)
        for agent in neighbors:
            #print("\n{0} is a Building: {1}\nis a Civilian {2}".format(type(agent), type(agent) == Building.Building, type(agent) == Civilian))
            if type(agent) == Civilian or type(agent) == Building.Building:
                # Pick out this agent to be victimized

                return agent

        return False

    def check_for_police(self):
        """Check for police around a position, but only in cells the criminal can currently see in their neighborhood

        Params:
            pos (list): A list where [0] is x and [1] is y
            neighborhood (list): A list of cells, assumed to be the criminal's neighborhood
        Returns:
            True if there are police in proximity to pos that the Criminal can see in their neighborhood
        """
        #print("Are there any police around?")
        neighbors = self.environment.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=self.vision)

        for neighbor in neighbors:
            if type(neighbor) is Police:
                # There are Police
                #print("Police are present, abort crime.")
                return True
        # No police
        return False

    def increase_propensity(self):
        """Increase the propensity of the criminal. Can be simple or maybe more complicated."""
        self.crime_propensity += 1
        return

    def join_agents_coalition(self, agent):
        """If not in coalition join it. If in one, merge them. Assumes authority to do so in latter case.

        Returns:
            True, if successfully joins/merges coalition
        """

        if self.network is not None:
            # In a coalition already, try to merge the other coalition into ours
            if agent.network is None:
                # Let the solo agent join our coalition
                return self.network.add_member(agent)
            elif self.network is not agent.network:
                # Merge the two DIFFERENT coalitions
                return self.network.merge(agent.network)
        elif agent.network is None:
            # Other agent is also not in a coalition, create a new one.
            coalition = self.environment.new_coalition()
            coalition.add_member(self)
            coalition.add_member(agent)
            return True
        else:
            # Not currently in a network, try to join the coalition
            return agent.network.add_member(self)

    def leave_coalition(self):
        """Let an agent leave their coalition.

        FIXME Should probably live in Agent
        """
        if self.network is None:
            print("\nError: Criminal tried to leave coalition when not in one.\n")
            return

        # Leave coalition
        self.network.remove_member(self)

    def try_to_join_nearby_coalitions(self):
        """Look for criminals around to coerce into joining forces."""
        # Can only join forces at a maximum specified distance
        radius = self.environment.config['coalition_merge_distance']

        potential_partners = self.environment.grid.get_neighbors(pos=self.pos, radius=radius,
                                                           moore=True, include_center=True)
        if potential_partners:
            random.shuffle(potential_partners)  # randomize
            for agent in potential_partners:
                if type(agent) is Criminal and agent is not self:
                    # Agent is a criminal - join forces
                    if self.join_agents_coalition(agent):
                        return


    def update_coalition_status(self):
        """General workhorse for coalition stuff.
.
        Check if personal propensity is greater than required threshold. If not, try to join nearby coalitions. If it \
        is, split from any coalitions this criminal is in.
        """

        if not self.environment.has_sufficient_propensity(self):
            # Propensity too low, look for others to join coalition with
            self.try_to_join_nearby_coalitions()
        elif self.environment.can_be_solo(self):
            # Propensity is high enough to go solo, split from current coalition
            if self.network is not None:
                self.leave_coalition()
        return


    def walk_to_avoid(self, coordinates, role_to_avoid):
        """Walk one cell towards a set of coordinates, using only cardinal directions (North/South or West/East"""
        x, y = self.pos  # Current position
        x_target, y_target = coordinates  # Target position
        dx, dy = x_target - x, y_target - y  # Distance from target in terms of x/y
        next_moves = self.environment.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        next_moves = [cell for cell in filter(lambda x: self.environment.grid.can_agent_occupy_cell(x), next_moves)]
        random.shuffle(next_moves)

        # Scale dx/dy to -1/1 for use as coordinate move
        if dx != 0 and dy != 0:
            # Agent needs to go vertical and horizontally, choose one randomly
            if random.random() < 0.5:
                # The agents or buildings in the next position
                agents_buildings = self.environment.grid.get_cell_list_contents((dx / abs(dx) + x, y))
                # Check if the next position is avoided
                avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
                if not avoid:
                    # Move horizontally
                    dest_x = int(x + dx / abs(dx))
                    dest_y = int(y)
                else:
                    # move randomly and avoid the specified roles
                    dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)
                    
            else:
                agents_buildings = self.environment.grid.get_cell_list_contents((x, dy / abs(dy) + y))
                avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
                if not avoid:
                    # Move vertically
                    dest_y = int(y + dy / abs(dy))
                    dest_x = int(x)
                else:
                    dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)
                    
        elif dx == 0 and dy == 0:
            # Agent is at destination
            return True
        elif dx == 0:
            agents_buildings = self.environment.grid.get_cell_list_contents((x, dy / abs(dy) + y))
            avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
            if not avoid:
                # Agent only needs to move vertically
                dest_y = int(y + dy / abs(dy))
                dest_x = int(x)
            else:
                dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)
            
        elif dy == 0:
            agents_buildings = self.environment.grid.get_cell_list_contents((x, dy / abs(dy) + y))
            avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
            if not avoid:
                # Agent only needs to move horizontally
                dest_x = int(x + dx / abs(dx))
                dest_y = int(y)
            else:
                dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)

        self.environment.grid.move_agent(self, (dest_x, dest_y))
        # FIXME Check if there?
        return x_target == dest_x and y_target == dest_y
    
    
    def target_building(self):
        target = self.environment.agents['buildings'][0]
        risk = target.attractiveness + math.sqrt((self.pos[0]-target.pos[0])**2 + (self.pos[1]-target.pos[1])**2)
        for i in range(len(self.environment.buildings)):
            dist = math.sqrt((self.pos[0]-self.environment.agents['buildings'].pos[0])**2 + (self.pos[1]-self.environment.agents['buildings'][i].pos[1])**2)
            if(risk > self.environment.agents['buildings'].attractiveness + dist):
                risk = self.environment.agents['buildings'].attractiveness + dist
                target = self.environment.agents['buildings'][i]
        return target

    def update_attractiveness(self):
        neighbor_buildings = list(
                filter(
                    lambda x: isinstance(x, Building),
                    self.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=1)))
        for building in neighbor_buildings:
            self.building_memory[building.uid] = building.attractiveness
        
            

class Civilian(Agent):
    def __init__(self, pos, model, resources, uid, route, utility = [], residence=None, workplace=None):
        super().__init__(self, pos, model, resources, uid, residence)
        self.pos = pos
        self.environment = model
        self.resources = resources
        self.uid = uid
        self.history_self = None
        self.history_others = None
        self.allies = None
        self.competitors = None
        self.memory = list()
        self.mental_map = dict()
        self.vision = random.randint(1, model.config['agent_vision_limit'])
        self.workplace = random.shuffle(self.environment.agents['commercial_buildings'])
        self.utility = utility
        self.residence = random.shuffle(self.environment.agents['residences'])
        self.route = tuple(self.residence.pos, self.workplace.pos)
        # Individuals who have tried to rob this civilian
        self.criminal_memory = list()
        self.num_routes_completed = 0
        # Attractiveness for each building
        self.building_memory = list()
        return
    

    def __str__(self):
        return "Civilian " + str(self.uid)

    def step(self):
        if len(self.memory) > 0:
            self.walk_and_avoid()
        else:
            #self.random_move()
            self.walk_route()
        
        # add the buildings in the neighbourhood to the civilian's memory
        neighborhood = self.environment.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        
        for cell in neighborhood:
            for agent_building in self.environment.grid.get_cell_list_contents(cell):
                if type(agent_building) is Building:
                    self.add_to_building_memory(agent_building)      
        if(self.num_routes_completed % 2 == 0):
            if(self.pos == self.workplace.pos):
                self.num_routes_completed += 1
                self.utility.append(b.utility_function(self))

        else:    
            if(self.pos == self.residence.pos):
                self.num_routes_completed += 1
                self.utility.append(b.utility_function(self))
                
        return
    
    def walk_route(self):
        
        if(self.num_routes_completed % 2 == 0):
            self.walk_to(self.workplace.pos)
        else:
            self.walk_to(self.residence.pos)
        
        return

    def walk_and_avoid(self):
        """Random walk, but avoid cells with agents in memory

        Returns:
            True if successfully moved
            False if couldn't move anywhere
        """

        # FIXME CIVILIAN move choosing does not consider criminals they can see more than one space away
        # doesn't consider moving towards a criminal they can see
        next_moves = self.environment.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        next_moves = [cell for cell in filter(lambda x: self.environment.can_agent_occupy_cell(x), next_moves)]

        random.shuffle(next_moves)
        for cell in next_moves:
            if sum(agent in self.memory for agent in self.environment.grid.get_cell_list_contents(cell)):
                continue

            else:
                # Move to this cell where there is nobody we remember
                self.environment.grid.move_agent(self, cell)
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
        self.environment.call_police(self, agent)
        return
    
    def add_to_building_memory(self, building):
        """Add a building to the civilian's momory.
        """
        self.building_memory.append(building)
        self.building_memory = list(set(self.building_memory)) # remove repeats
        
    
    def walk_to_avoid(self, coordinates, role_to_avoid):
        """Walk one cell towards a set of coordinates, using only cardinal directions (North/South or West/East"""
        x, y = self.pos  # Current position
        x_target, y_target = coordinates  # Target position
        dx, dy = x_target - x, y_target - y  # Distance from target in terms of x/y
        next_moves = self.environment.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        next_moves = [cell for cell in filter(lambda x: self.environment.grid.can_agent_occupy_cell(x), next_moves)]
        random.shuffle(next_moves)

        # Scale dx/dy to -1/1 for use as coordinate move
        if dx != 0 and dy != 0:
            # Agent needs to go vertical and horizontally, choose one randomly
            if random.random() < 0.5:
                # The agents or buildings in the next position
                agents_buildings = self.environment.grid.get_cell_list_contents((dx / abs(dx) + x, y))
                # Check if the next position is avoided
                avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
                if not avoid:
                    # Move horizontally
                    dest_x = int(x + dx / abs(dx))
                    dest_y = int(y)
                else:
                    # move randomly and avoid the specified roles
                    dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)
                    
            else:
                agents_buildings = self.environment.grid.get_cell_list_contents((x, dy / abs(dy) + y))
                avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
                if not avoid:
                    # Move vertically
                    dest_y = int(y + dy / abs(dy))
                    dest_x = int(x)
                else:
                    dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)
                    
        elif dx == 0 and dy == 0:
            # Agent is at destination
            return True
        elif dx == 0:
            agents_buildings = self.environment.grid.get_cell_list_contents((x, dy / abs(dy) + y))
            avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
            if not avoid:
                # Agent only needs to move vertically
                dest_y = int(y + dy / abs(dy))
                dest_x = int(x)
            else:
                dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)
            
        elif dy == 0:
            agents_buildings = self.environment.grid.get_cell_list_contents((x, dy / abs(dy) + y))
            avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
            if not avoid:
                # Agent only needs to move horizontally
                dest_x = int(x + dx / abs(dx))
                dest_y = int(y)
            else:
                dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)

        self.environment.grid.move_agent(self, (dest_x, dest_y))
        # FIXME Check if there?
        return x_target == dest_x and y_target == dest_y


class Police(Agent):
    """A Police Officer - an agent that is dispatched to Crime Scenes and arrests evil-doers

    """

    def __init__(self, pos, model, resources=[], uid=None, network=None, hierarchy=None, history_self=[],
                 history_others=[], policy=None, allies=[], competitors=[], residence=None):
        super().__init__(self, pos, model, resources, uid, network, hierarchy, policy, residence=None)
        self.pos = pos
        self.environment = model
        self.resources = resources
        self.uid = uid
        self.history_self = history_self
        self.history_others = history_others
        self.allies = allies
        self.competitors = competitors
        self.dispatch_coordinates = None
        self.target = None
        self.vision = random.randint(1, model.config['agent_vision_limit'])
        self.pd = None
        self.arrest_radius = model.config['police_arrest_radius']

    def __str__(self):
        return "Police " + str(self.uid)

    def step(self):
        """One time unit in the simulation, decide what actions to take"""

        # Check if this Police has an assignment
        if self.dispatch_coordinates is not None:
            criminal_in_sight = self.scan_for_target()  # update dispatch coordinates if this police can see their target

            if self.walk_to(self.dispatch_coordinates):
                # Arrived at crime scene / target coordinates
                self.initiate_investigation()

            elif not criminal_in_sight:
                # Did not arrive at crime scene, search for target again on the way there.
                self.scan_for_target()
        else:
            # No dispatch assignment, patrol randomly
            self.random_move()

    def initiate_investigation(self):
        # Check if target is in same cell - which should be the dispatch coordinates
        print("Officer arrived at the crime scene")

        if self.target in self.environment.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=self.arrest_radius):
            # Target is within the police's arrest radius
            # if self.arrest_radius is 0, then the police and the target is in the same cell
            print("Attempting arrest at {0} for criminal at {1}".format(self.pos, self.target.pos))
            if self.environment.attempt_arrest(criminal=self.target, police=self):
                pass


        elif not self.scan_for_target():
            # Drop Investigation
            # TODO A timer for patience? i.e. moving randomly until patience runs out.
            print("Officer could not find Criminal %s, they give up!" % self.target.uid)
            self.drop_investigation()


    def drop_investigation(self):
        # Remove from other police officer's who are chasing the same target
        self.environment.grid.move_agent(self, self.pd.pos)  # police goes to the station with criminal, for processing



    def scan_for_target(self):
        # Check around officer if the target is in sight
        # FIXME Scanning is broken!
        # FIXME Maybe use the model to determine distance instead of scanning - this includes opportunity for police to miss \
        # FIXME the target or something - gives control to the model?
        agents = self.environment.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=self.vision)
        for agent in agents:
            if agent is self.target:
                #print("Spotted target!")
                self.dispatch_coordinates = agent.pos
                return True
        # Target not spotted, fail
        return False
    
    def walk_to_avoid(self, coordinates, role_to_avoid):
        """Walk one cell towards a set of coordinates, using only cardinal directions (North/South or West/East"""
        x, y = self.pos  # Current position
        x_target, y_target = coordinates  # Target position
        dx, dy = x_target - x, y_target - y  # Distance from target in terms of x/y
        next_moves = self.environment.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        next_moves = [cell for cell in filter(lambda x: self.environment.grid.can_agent_occupy_cell(x), next_moves)]
        random.shuffle(next_moves)

        # Scale dx/dy to -1/1 for use as coordinate move
        if dx != 0 and dy != 0:
            # Agent needs to go vertical and horizontally, choose one randomly
            if random.random() < 0.5:
                # The agents or buildings in the next position
                agents_buildings = self.environment.grid.get_cell_list_contents((dx / abs(dx) + x, y))
                # Check if the next position is avoided
                avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
                if not avoid:
                    # Move horizontally
                    dest_x = int(x + dx / abs(dx))
                    dest_y = int(y)
                else:
                    # move randomly and avoid the specified roles
                    dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)
                    
            else:
                agents_buildings = self.environment.grid.get_cell_list_contents((x, dy / abs(dy) + y))
                avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
                if not avoid:
                    # Move vertically
                    dest_y = int(y + dy / abs(dy))
                    dest_x = int(x)
                else:
                    dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)
                    
        elif dx == 0 and dy == 0:
            # Agent is at destination
            return True
        elif dx == 0:
            agents_buildings = self.environment.grid.get_cell_list_contents((x, dy / abs(dy) + y))
            avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
            if not avoid:
                # Agent only needs to move vertically
                dest_y = int(y + dy / abs(dy))
                dest_x = int(x)
            else:
                dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)
            
        elif dy == 0:
            agents_buildings = self.environment.grid.get_cell_list_contents((x, dy / abs(dy) + y))
            avoid = sum([type(agent) in role_to_avoid for agent in agents_buildings])
            if not avoid:
                # Agent only needs to move horizontally
                dest_x = int(x + dx / abs(dx))
                dest_y = int(y)
            else:
                dest_x, dest_y = self.random_move_and_avoid_role(role_to_avoid)

        self.environment.grid.move_agent(self, (dest_x, dest_y))
        # FIXME Check if there?
        return x_target == dest_x and y_target == dest_y


