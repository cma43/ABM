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
    pos = None

    # The occupant(s) of the building
    residents = list()

    # The environment where this building exists
    environment = None


    def __init__(self, environment, pos = None, residents=None, attractiveness=None):
        if not isinstance(pos, tuple):
            raise ValueError("Location must be a tuple: e.g. (x, y)")

        # Location /Environment is required
        self.environment = environment

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
        """Add an agent to the Building's resident list and update the agent's dwelling status."""
        self.residents.append(agent)
        agent.set_residence(self)



    def drop_resident(self, agent):
        """Remove an agent from this building's resident list and update that agent's dwelling status"""
        try:
            self.residents.remove(agent)
            agent.set_residence(None)
        except Exception as e:
            raise e

    def improve_attractiveness(self):
        """Improve the attractiveness of the building according to environment"""
        self.environment.improve_building_attractiveness(self)

class CommercialBuilding(Building):
    """Represents a Commercial Building."""

    def __init__(self, environment, pos = None, residents=None, attractiveness=None):
        Building.__init__(self, environment, pos, residents, attractiveness)
        employees = list()

    def add_employee(self, employee):
        """Add an employee to work at this store."""
        self.employees.append(employee)

    def remove_employee(self, employee):
        """Fire an employee who works at this store."""
        try:
            self.employees.remove(employee)
        except Exception as e:
            print(e)

