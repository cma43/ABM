from Coalition import Coalition
import random
import itertools
from rat_agents import Police, Criminal, Civilian

class PoliceDepartment(Coalition):
    """A group of Police officers who coordinate together to stop EeeeeVIL.
       They have a 'base' a.k.a. the physical police department.
    """

    def __init__(self, uid, environment):
        super().__init__(uid, environment)
        
        # Set position to a pre-specified 'police department' where criminals
        # will be held if they are caught. If random, choose a coordinate such
        # as (2,2), (7,7), etc.
        
        # TODO Allow the user to specify a position for the police department object
        # if they don't want to randomly choose a police department position
        
        if(self.environment.config['police_dept_start'] == 'default'):
            self.pos = environment.grid.width // 2, environment.grid.height // 2
        elif(self.environment.config['police_dept_start'] == 'random'):
            x_coord = list(range(environment.grid.width))
            y_coord = list(range(environment.grid.height))
            
            coord_pairs = tuple(itertools.product(x_coord, y_coord))
            
            self.pos = random.choice(coord_pairs)
            
        self.environment.grid.place_agent(self, self.pos)

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
                return officer

    def remove_target(self, target):
        """Call off the search for a target."""
        for police in self.members:
            if police.target is target:
                police.target = None
                police.dispatch_coordinates = None
