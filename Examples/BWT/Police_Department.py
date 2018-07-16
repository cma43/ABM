from Base.Coalition import Coalition
import random
import logging

class PoliceDepartment(Coalition):
    """A group of Police agents who coordinate to patrol pre-assigned areas of the
       map and catch criminals.
       Agents of Police subclass have a 'base', i.e., the physical police department.


    """

    def __init__(self, uid, environment):
        super().__init__(uid, environment)
        self.pos = environment.grid.width // 2, environment.grid.height // 2
        self.environment.grid.place_agent(self, self.pos)

    def dispatch(self, victim, target_agent):
        """Dispatch an officer to talk to a Civilian who called in about a robbery.

        :param victim: The Civilian agent who called.
        :param target_agent: The Police agent responding.
        :return: None.
        """
        officer = self.find_closest_free_officer(victim.pos)

        if officer is None:
            logging.info("No available officers to dispatch")
            return False

        officer.dispatch_coordinates = victim.pos
        officer.target = target_agent
        logging.info("Officer dispatched to Crime Scene")

    def find_closest_free_officer(self, pos):
        """Find the closest officer in the effective range of police officers.

        :param pos: An (x,y) tuple for the center point of a search radius.

        Note: Search radius specified by 'effective_police_radius' in the environment
        config file.


        """
        police = self.environment.grid.get_neighbors(pos, moore=True,
                                                     include_center=True,
                                                     radius=self.environment.config['effective_police_radius'])
        police = list(filter(lambda x: x in self.members, police))

        random.shuffle(police)
        for officer in police:
            if officer.dispatch_coordinates is None:
                return officer

    def remove_target(self, target):
        """Call off the search for a target.

        :param target: An Criminal subclass agent that Police agents are searching for.


        """
        for police in self.members:
            if police.target is target:
                police.target = None
                police.dispatch_coordinates = None
