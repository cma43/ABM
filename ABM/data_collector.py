

class dataManager(object):
    """Handles the functions for collecting episodic information and for summarizing it."""

    def __init__(self, num_episodes, num_steps):
        self.num_episodes = num_episodes
        self.num_steps = num_steps

        self.data_in_sim = list()


    def start_new_episode(self, environment):
        """Creates a new dataSim object that will collect information from the specified environment."""






class dataSim(object):
    """
    Collects data from a single simulation.
    """

    # FIXME Add support to include/drop desired data

    def __init__(self, env, num_runs, animation_moving_average_coefficient=0.9, do_animation=False):
        # The environment to get data from
        self.env = env

        # Flag for doing animations
        self.do_animation = do_animation
        self.animation_moving_average_coefficient = animation_moving_average_coefficient

        # The number of steps the simulation is being run for
        self.num_runs = num_runs

        # Use to keep track of movement patterns of each Role's population
        self.police_loc = np.zeros((env.config['grid_width'] + 1, env.config['grid_height'] + 1))
        self.civ_loc = np.zeros((env.config['grid_width'] + 1, env.config['grid_height'] + 1))
        self.criminal_loc = np.zeros((env.config['grid_width'] + 1, env.config['grid_height'] + 1))

        # Initial State info
        self.init_police_loc = np.zeros((env.config['grid_width'] + 1, env.config['grid_height'] + 1))
        self.init_civilian_loc = np.zeros((env.config['grid_width'] + 1, env.config['grid_height'] + 1))
        self.init_criminal_loc = np.zeros((env.config['grid_width'] + 1, env.config['grid_height'] + 1))

        # A single civilians location over time
        self.single_loc = np.zeros((env.config['grid_width'] + 1, env.config['grid_height'] + 1))

        # The locations where crimes occurred over the simulation
        self.crime_loc = np.zeros((env.config['grid_width'] + 1, env.config['grid_height'] + 1))

        # How many times each citizen is robbed over the sim
        self.civilian_times_robbed = np.zeros((env.config['num_civilians']))

        # Essentially the number of unique criminals that rob each citizen
        self.civilian_memory_length = np.zeros((env.config['num_civilians']))

        # Cumulative crimes over time
        self.total_crimes_at_step = np.zeros(num_runs)

        # moving heat maps, civilians
        self.civ_heat_maps = []
        self.criminal_heat_maps = []
        self.police_heat_maps = []
        self.crime_heat_maps = []


    def collect_init_state(self):
        """Collect and store information about the initial state of the environment
        """
        for police in self.env.police:
            self.init_police_loc[police.x][police.y] += 1

        for civilian in self.env.civilians:
            self.init_civilian_loc[civilian.x][civilian.y] += 1

        for criminal in self.env.criminals:
            self.init_criminal_loc[criminal.x][criminal.y] += 1


    def collect_step_data(self, step_number):
        """
        Collect and store data from the last executed tick() in an environment
        """

        # Collect Location Data for Police, Civilians, Criminals, and Crimes this turn
        for police in self.env.police:
            self.police_loc[police.x][police.y] += 1

        for civ in self.env.civilians:
            self.civ_loc[civ.x][civ.y] += 1
            self.civilian_times_robbed[civ.uid]

        for criminal in self.env.criminals:
            self.criminal_loc[criminal.x][criminal.y] += 1

        for location in self.env.crimes_this_turn:
            self.crime_loc[location[0]][location[1]] += 1

        # Total Crime data
        if step_number > 0:
            self.total_crimes_at_step[step_number] = self.total_crimes_at_step[step_number - 1] + len(self.env.crimes_this_turn)
        else:
            self.total_crimes_at_step[0] = len(self.env.crimes_this_turn)

        # Collect animation frames
        if self.do_animation:
            self.add_to_animation_frames(self.animation_moving_average_coefficient)

    def add_to_animation_frames(self, mac):
        """
        Adds to the animation frames for the first simulation.

        :param mac (float) 0-1 moving average coefficient


        FIXME Possibly pass in the moving average coefficient?
        FIXME Can this be more efficient?
        :return:
        """

        if len(self.civ_heat_maps) <= 0:
            # First step - create blank slate
            self.civ_heat_maps.append(np.zeros((self.env.grid_width + 1, self.env.grid_height + 1)))
            self.criminal_heat_maps.append(np.zeros((self.env.grid_width + 1, self.env.grid_height + 1)))
            self.police_heat_maps.append(np.zeros((self.env.grid_width + 1, self.env.grid_height + 1)))

        else:
            # Apply moving average coefficient to last frame
            self.civ_heat_maps.append(self.civ_heat_maps[-1] * mac)
            self.criminal_heat_maps.append(self.criminal_heat_maps[-1] * mac)
            self.police_heat_maps.append(self.police_heat_maps[-1] * mac)

        # Now update where agents actually are
        for civ in self.env.civilians:
            self.civ_heat_maps[-1][civ.x][civ.y] = 1  # animation data, base locations
        for criminal in self.env.coalitions:
            self.criminal_heat_maps[-1][criminal.x][criminal.y] = 1
        for police in self.env.police:
            self.police_heat_maps[-1][police.x][police.y] = 1

        return

def normalize(location_array):
    """
    Helper function that rescales the values in a 2D array `location_array` to be between 0 and 1, where the max value
    seen in the array is coded to 1.

    :param location_array: A numpy 2D array
    :return: The rescaled array
    """
    #width, height = location_array.shape
    max_value = max(map(max, location_array))
    if max_value == 0: return location_array # Avoid divide by 0 error
    location_array = list(map(lambda x: x / max_value, location_array))
    return location_array
