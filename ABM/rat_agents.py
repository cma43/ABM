from agent_cma_zl import Agent
import random


class Criminal(Agent):
    def __init__(self, pos, model, resources, uid, network=None, hierarchy=None, history_self=[],
                 history_others=[], policy=None, allies=[], competitors=[], crime_propensity=None):
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
        self.update_coalition_status()

        # Look for victims if we have enough propensity
        if self.environment.has_sufficient_propensity(self):
            immediate_victim = self.look_for_victim(radius=0, include_center=True)
            if immediate_victim and not self.check_for_police():
                # There is a potential victim in the same cell, and no police around - try to rob them
                print("Attempting robbery at %s" % str(self.pos))
                self.commit_crime(immediate_victim)
                return

            else:  # Look further away for victims if there are none in the same cell
                for radius in range(1, self.vision+1):
                    potential_victim = self.look_for_victim(radius=radius, include_center=False)

                    if potential_victim:
                        print("Possible victim at %s" % str(potential_victim.pos))

                        # Found a victim
                        if self.walk_to(potential_victim.pos) and not self.check_for_police():
                            # FIXME should criminals be able to move and commit crimes in the same turn?
                            self.commit_crime(potential_victim)
                            return
                        else:
                            # Agent moved, so end step
                            return

        # Couldn't find victim, or insufficient propensity
        self.random_move_and_avoid_role(Police)
        return

    def commit_crime(self, victim):
        """Commit a crime against a random agent in the current position"""
        # FIXME criminals seem to be very stupid
        # Rob half of their resources if model deems the crime successful
        # This call to the model is an attempt to keep the environment in charge of interaction rules
        self.environment.attempt_crime(self, victim)


    def look_for_victim(self, radius, include_center):
        """Look in the neighborhood for a potential victim to rob.

        :return: An agent object
                 False, if no victims in sight
        """
        neighbors = self.environment.grid.get_neighbors(self.pos, True,  radius=radius, include_center=include_center)
        random.shuffle(neighbors)

        for agent in neighbors:
            if type(agent) == Civilian:
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
        print("Are there any police around?")
        neighbors = self.environment.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=self.vision)

        for neighbor in neighbors:
            if type(neighbor) is Police:
                # There are Police
                print("Police are present, abort crime.")
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


class Civilian(Agent):
    def __init__(self, pos, model, resources, uid):
        super().__init__(self, pos, model, resources, uid)
        self.pos = pos
        self.environment = model
        self.resources = resources
        self.uid = uid
        self.history_self = None
        self.history_others = None
        self.allies = None
        self.competitors = None
        self.memory = list()
        self.vision = random.randint(1, model.config['agent_vision_limit'])

        # Individuals who have tried to rob this civilian
        self.criminal_memory = list()
        return

    def __str__(self):
        return "Civilian " + str(self.uid)

    def step(self):
        if len(self.memory) > 0:
            self.walk_and_avoid()
        else:
            self.random_move()
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


class Police(Agent):
    """A Police Officer - an agent that is dispatched to Crime Scenes and arrests evil-doers

    """

    def __init__(self, pos, model, resources=[], uid=None, network=None, hierarchy=None, history_self=[],
                 history_others=[], policy=None, allies=[], competitors=[]):
        super().__init__(self, pos, model, resources, uid, network, hierarchy, policy)
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

        if self.pos[0] == self.target.pos[0] and self.pos[1] == self.target.pos[1]:
            # Target is in same cell!
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
                print("Spotted target!")
                self.dispatch_coordinates = agent.pos
                return True
        # Target not spotted, fail
        return False
