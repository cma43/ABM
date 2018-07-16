import random

class Building:
    """This object represents a building in an environment.

    Only one agent may live in a building. The building has an "attractiveness" attribute that is affected by \
    crime. The more crime that occurs at this building or directly adjacent affects the attractiveness and causes \
    crime to be more likely at this building.

    Attractiveness is randomly assigned if not specified
    """

    def __str__(self):
        return "Building at " + str(self.pos)

    # A measure of attractiveness on a scale from 0-1
    attractiveness = random.random()

    # The residences location, a tuple of integers (x, y)
    pos = ()

    # The occupant(s) of the building
    residents = list()

    # The environment where this building exists
    environment = None


    def __init__(self, environment, uid, pos = None, residents=None, attractiveness=None):
        """
        :param environment: The environment the building is in.
        :param uid: The unique id of the building.
        :param pos: The position tuple of the building.
        :param residents: The list of residents of the building.
        :param attractiveness: The attractiveness of the builiding.
        """
        if not isinstance(pos, tuple):
            raise ValueError("Location must be a tuple: e.g. (x, y)")

        # Location /Environment is required
        self.environment = environment
        self.uid = uid
        self.pos = pos
        if self.pos is None:
            # Choose an unoccupied position on grid
            while(True):
                rand_pos = (random.randrange(0, environment.grid.width),
                            random.randrange(0, environment.grid.height))

                # Only allow one building per coordinate
                contents = environment.grid.get_cell_list_contents(rand_pos)
                contents = list(filter(lambda x: isinstance(x, Building), contents))

                if len(contents) == 0:
                    self.pos = rand_pos
                    break

        if residents is not None:
            # Add residents to resident list
            self.residents.append(residents)

        if attractiveness is not None:
            self.attractiveness = attractiveness


    def add_resident(self, agent):
        """Add an agent to the Building's resident list and update the agent's dwelling status.
        :param agent: An agent to be added as a resident to a building
        :type agent: An instance of the Agent class
        """
        self.residents.append(agent)
        agent.set_residence(self)



    def drop_resident(self, agent):
        """Remove an agent from this building's resident list and update that agent's dwelling status
        :param agent: An Agent object
        :type agent: An instance of the Agent class
        """
        try:
            self.residents.remove(agent)
            agent.set_residence(None)
        except Exception as e:
            raise e

    def improve_attractiveness(self):
        """Improve the attractiveness of the building according to environment"""
        self.environment.improve_building_attractiveness(self)

class CommercialBuilding(Building):
    """Represents a Commercial Building. Objects of this class
       are initilialized with an environment, a unique ID, a position in a
       2D plane, a list of employees for this building, and its initial assignment for
       the state of the building called 'attractiveness'
    """

    def __init__(self, environment, uid, pos = (), residents=None, attractiveness=None):
        """
        :param environment: The environment the building is in.
        :param uid: The unique id of the building.
        :param pos: The position tuple of the building.
        :param residents: The list of residents of the building.
        :param attractiveness: The attractiveness of the builiding.
        """
        Building.__init__(self, environment, uid, pos, residents, attractiveness)
        employees = list()

    def add_employee(self, employee):
        """Add an employee to work at this store.
            :param employee: An Agent object.
            :type employee: An instance of the Agent class; should be a Civilian subclass agent.
        """
        self.employees.append(employee)

    def remove_employee(self, employee):
        """Fire an employee who works at this store.
            :param employee: An Agent object.
            :type employee: An instance of the Agent class; should be a Civilian subclass agent.
        """
        try:
            self.employees.remove(employee)
        except Exception as e:
            print(e)
