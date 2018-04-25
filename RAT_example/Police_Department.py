from ABM.Coalition import Coalition
import random
from RAT_example.rat_agents import Police, Criminal, Civilian

class PoliceDepartment(Coalition):
    """A group of Police officers who coordinate together to stop EeeeeVIL.
       They have a 'base' a.k.a. the physical police department.
    """

    def __init__(self, uid, environment):
        super().__init__(uid, environment)
        self.pos = environment.grid.width // 2, environment.grid.height // 2
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
