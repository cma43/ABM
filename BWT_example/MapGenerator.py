from random import randrange, shuffle
from BWT_example.Building import Building, CommercialBuilding


class MapGenerator:

    def __init__(self, environment):
        self.environment = environment
        self.width = environment.grid.width
        self.height = environment.grid.height
        self.available_cells = list()
        self.available_road_cells = list()
        self.available_building_cells = list()


    def generate_map(self):
        """Create an urban map with roads and residences."""

        # Create main streets first
        self.create_main_streets()

        # Then create the commercial buildings in the center of town
        self.create_commercial_center()

        # Then create the neighborhoods that populate the rest of the city
        while(self.create_neighborhood()):
            pass

        # Clean up any invalid buildings that were created
        self.delete_inaccessible_buildings()



    def create_main_streets(self):
        middle_x_coord = self.width // 2
        middle_y_coord = self.height // 2

        ns_street = [Road([middle_x_coord, y_coord]) for y_coord in range(0, self.height-1)]
        we_street = [Road([x_coord, middle_y_coord]) for x_coord in range(0, self.width-1)]

        for road in ns_street:
            self.place_road(road)
        for road in we_street:
            self.place_road(road)

    def create_commercial_center(self):
        """Create a commercial hub in the center of the city"""

        approx_center = (self.width // 2, self.height // 2)
        potential_commercial_cells = self.filter_potential_commercial_cells(
            self.environment.grid.get_neighborhood(approx_center, moore=True, include_center=False),
            list())

        for i in range(self.width * self.height // (100//3)):
            # Make the commercial center make up 3% of the map
            if len(potential_commercial_cells) == 0:
                # Stop if there are no more valid locations
                return

            # Randomly place a commercial building in one of the available cells, update potential cell list
            shuffle(potential_commercial_cells)
            building_pos = potential_commercial_cells[0]
            new_commercial_building = CommercialBuilding(self.environment, pos=building_pos)
            potential_commercial_cells = self.place_commercial_building(new_commercial_building,
                                                                        potential_commercial_cells)

        # Surround commercial center with a layer of roads
        for building in self.environment.commercial_buildings:
            for neighbor_cell in self.environment.grid.get_neighborhood(building.pos, moore=True):
                if self.environment.grid.is_cell_empty(neighbor_cell):
                    if self.num_adj_commercial_buildings(neighbor_cell) < 4:
                        self.place_road(Road(neighbor_cell))
                    else:
                        try:
                            self.available_cells.remove(neighbor_cell)
                        except:
                            pass

    def delete_inaccessible_buildings(self):
        """Cleans up any buildings that were created accidentally in inaccessble places"""
        def num_adj_buildings(pos):
            """Helper function that returns number of immediately adjacent commercial buildings"""
            neighborhood = self.environment.grid.get_neighborhood(pos, moore=False, include_center=False)

            adj_num = 0
            num_cells = 0
            for cell in neighborhood:
                num_cells += 1
                # Check contents of each neighbor
                if not self.environment.grid.is_cell_empty(cell):
                    contents = self.environment.grid.get_cell_list_contents(cell)
                    for agent in contents:
                        if type(agent) is Building or type(agent) is CommercialBuilding:
                            # check that cell is not empty and contains a commercial building in it
                            adj_num += 1
                            break
            return adj_num, num_cells

        def is_inacessible(cell):
            """Helper function, converts to boolean"""
            adj, count = num_adj_buildings(cell)
            return adj == count

        # Main Function
        for building in self.environment.residences:
            if is_inacessible(building.pos):
                self.environment.grid.remove_agent(building)
                self.environment.residences.remove(building)

        for building in self.environment.commercial_buildings:
            if is_inacessible(building.pos):
                self.environment.grid.remove_agent(building)
                self.environment.commercial_buildings.remove(building)


    def place_commercial_building(self, building, potential_cells):
        """Mirror of place_road, but places a commercial building as well and adds to the environment's list of
        commercial buildings

        :param potential_cells: a list of cells that commercial buildings can be placed in, update it with the \
                                cells that are available after placing this building
        """
        if not self.environment.grid.is_cell_empty(building.pos):
            return False

        # Place building
        self.environment.grid.place_agent(agent=building, pos=building.pos)
        self.environment.commercial_buildings.append(building)

        # Identify new available locations for commercial buildings around this one
        newly_available_cells = self.environment.grid.get_neighborhood(building.pos, moore=False, include_center=False)
        potential_cells = self.filter_potential_commercial_cells(newly_available_cells, potential_cells)

        # Remove this cell from the potential list
        potential_cells.remove(building.pos)

        return potential_cells


    def filter_potential_commercial_cells(self, new_cells, all_cells):
        """Manages the list of cells that commercial cells can be placed in.

        Current rules: No more than 3 adjacent commercial buildings
                       Must be EMPTY (no existing roads or buildings in cell)

        :param new_cells: The list of cells to filter and add to the all_cells
        :param all_cells: The master list of potential cells for commercial buildings

        :return The updated all_cells list of potential commercial building locations
        """

        # List of cells that are valid
        valid_cells = list()



        def wont_cut_off_other_commercial_buildings(pos):
            """Helper function that ensures other commercial buildings won't be cutoff if a commercial building is
            placed at pos"""
            for adj_cell in self.environment.grid.get_neighborhood(pos, moore=False, include_center=False):
                # Check if the adj_cell is already touching at most 3 commercial buildings - can't cut anybody off
                if self.num_adj_commercial_buildings(adj_cell) == 3:
                    return False

            return True

        # Check each cell in the new_cells list for validity
        for cell in new_cells:

            if self.environment.grid.is_cell_empty(cell) and\
                    self.num_adj_commercial_buildings(cell) <= 3 and \
                    wont_cut_off_other_commercial_buildings(cell) and \
                    cell not in all_cells:
                # If cell is empty, surrounded by AT MOST 3 commercial buildings, won't cut off any other buildings,
                # and it not already in the potential list:
                # add it to that list of potential commercial buildings.
                all_cells.append(cell)

            else:
                try:
                    all_cells.remove(cell)
                except:
                    pass

        return all_cells

    def place_building(self, building):
        """ Place a residence building on the grid and add it to the environment list of residences,

            IFF cell is empty
        """
        if self.environment.grid.is_cell_empty(building.pos):
            self.environment.grid.place_agent(building, building.pos)
            self.environment.residences.append(building)
        else:
            try:
                self.available_cells.remove(building.pos)
            except:
                pass

    def place_road(self, road):
        """Places road on grid and updates the environment's road list

           IFF the road's position is empty on grid
         """

        # Check if space is empty
        if not self.environment.grid.is_cell_empty(road.pos):
            return False

        # Place Road
        self.environment.grid.place_agent(agent=road, pos=road.pos)

        # Add road to environment's road list
        self.environment.roads.append(road)

        # Update the list of cells where other things can be built
        self.update_available_cells(road)

    def create_neighborhood(self):
        """Randomly pick cell from available road cells and create a randomly sized neighborhood around that point"""
        if len(self.available_building_cells) == 0:
            return False
        # Pick cell
        shuffle(self.available_building_cells)

        neighborhood_origin = self.available_building_cells[0]
        if not self.creates_valid_building(neighborhood_origin):
            # If not a valid placement, remove location from list
            self.available_building_cells.remove(neighborhood_origin)
            # Retry!
            self.create_neighborhood()
            return True # Exit after neighborhood is created

        final_cells = [neighborhood_origin]
        self.available_building_cells.remove(neighborhood_origin)

        # Place building on origin
        self.place_building(Building(self.environment, neighborhood_origin))
        neighborhood_cells = self.environment.grid.get_neighborhood(neighborhood_origin, moore=True, include_center=True)

        # Create a random number of residence buildings in this neighborhood
        number_of_residences = randrange(2,6)

        for i in range(number_of_residences):
            while len(neighborhood_cells) > 0:
                shuffle(neighborhood_cells)
                if self.environment.grid.is_cell_empty(neighborhood_cells[0]):
                    self.place_building(Building(self.environment, neighborhood_cells[0]))
                    final_cells.append(neighborhood_cells[0])
                    try:
                        self.available_building_cells.remove(neighborhood_cells[0])
                    except:
                        pass

                    continue

                # Remove cell from list
                neighborhood_cells.remove(neighborhood_cells[0])

        # Fill surrounding space around buildings with roads!
        for building_location in final_cells:
            for surrounding_cell in self.environment.grid.get_neighborhood(building_location, moore=True):
                if self.environment.grid.is_cell_empty(surrounding_cell):
                    self.place_road(Road(surrounding_cell))

        return True

    def update_available_cells(self, agent):
        """Helper function that updates the list of available cells given an agent that was just placed on the grid.

           Determines the correct availability behavior based on the type of agent.
         """
        try:
            self.available_road_cells.remove(agent.pos)
        except:
            pass
        try:
            self.available_building_cells.remove(agent.pos)
        except:
            pass

        adj_cells = self.environment.grid.get_neighborhood(agent.pos, moore=False)
        surrounding_cells = self.environment.grid.get_neighborhood(agent.pos, moore=True)

        # Update available cells if agent is a road
        if type(agent) == Road:
            for cell in surrounding_cells:
                # Roads
                if self.creates_valid_road(cell) and cell not in self.available_road_cells:
                    self.available_road_cells.append(cell)

                # Buildings
                if self.creates_valid_building(cell) and cell not in self.available_building_cells:
                    self.available_building_cells.append(cell)

        if type(agent) == Building:
            for cell in surrounding_cells:
                # Roads
                if self.creates_valid_road(cell) and cell not in self.available_road_cells:
                    self.available_road_cells.append(cell)

                # Buildings
                if self.creates_valid_building(cell) and cell not in self.available_building_cells:
                    self.available_building_cells(cell)


    def creates_valid_road(self, center):
        """Returns True if creates valid road segment, i.e. does not create a square"""
        def at_least_one_cell_is_empty(cell_list):
            """Returns true if at least one cell in the list is empty or out of bounds"""
            for cell in cell_list:
                if self.environment.grid.out_of_bounds(cell) or self.environment.grid.is_cell_empty(cell):
                    return True
            return False

        def has_adj_road(center):
            """Helper:  returns true if there is a Road adjacent to the center cell."""
            for agent in self.environment.grid.get_neighbors(center, moore=False, include_center=False):
                if type(agent) == Road:
                    return True
            return False

        x, y = center

        # Check NE, NW, SE, SW areas:
        return \
            not self.environment.grid.out_of_bounds(center) and \
            self.environment.grid.is_cell_empty(center) and \
            has_adj_road(center) and \
            at_least_one_cell_is_empty([(x + 1, y + 1), (x + 1, y), (x, y + 1)]) and \
            at_least_one_cell_is_empty([(x - 1, y + 1), (x - 1, y), (x, y + 1)]) and \
            at_least_one_cell_is_empty([(x + 1, y - 1), (x + 1, y), (x, y - 1)]) and \
            at_least_one_cell_is_empty([(x - 1, y - 1), (x - 1, y), (x, y - 1)])

    def creates_valid_building(self, cell):
        """Helper Function that returns true if a cell is a valid location for a building

        Returns true if cell is empty and is not completelty surrounded by buildings, and doesn't cut off other buildings
        """
        def wont_cut_off_other_commercial_buildings(pos):
            """Helper function that ensures other commercial buildings won't be cutoff if a commercial building is
            placed at pos"""
            for adj_cell in self.environment.grid.get_neighborhood(pos, moore=False, include_center=False):
                # Check if the adj_cell is already touching at most 3 commercial buildings - can't cut anybody off
                if self.num_adj_commercial_buildings(adj_cell) == 3:
                    return False

            return True

        return \
            self.environment.grid.is_cell_empty(cell) and \
            self.num_adj_commercial_buildings(cell) != 4 and \
            wont_cut_off_other_commercial_buildings(cell)

    def num_adj_commercial_buildings(self, pos):
        """Helper function that returns number of immediately adjacent commercial buildings"""

        neighborhood = self.environment.grid.get_neighborhood(pos, moore=False, include_center=False)

        adj_num = 0
        for cell in neighborhood:
            # Check contents of each neighbor
            if not self.environment.grid.is_cell_empty(cell):
                contents = self.environment.grid.get_cell_list_contents(cell)
                for agent in contents:
                    if type(agent) is CommercialBuilding:
                        # check that cell is not empty and contains a commercial building in it
                        adj_num += 1

        return adj_num

class Road:
    """Represents a road on a map

    Agents may walk on them and roads may be connected to other roads.
    """

    # References to adjacent objects
    north = None
    east = None
    south = None
    west = None


    def __init__(self, pos):
        """

        :param pos: (tuple) x, y coordinates
        """
        self.pos = pos

    class Boundary:
        """Represents the grid boundary"""

        def __init__(self):
            pass

