"""
Run a specified number of simulaiton "batches" for a specific number of turns or until a terminal condition has been
reached within the simulation.

FIXME Add support for collecting specified data (e.g. location data, number of crimes) In the future, we may want \
FIXME certain data but not other computationally intensive stuff.

Created: March 9, 2018
Author: Chris Nobblitt
"""

from ABM import environment as env
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

class batchManager(object):
    """
    Manages batch runs and data collection among runs
    """

    def __init__(self, num_steps, num_batches, do_animation=False, animation_moving_average_coefficient=0.7):
        # Number of steps to run in each simulation
        self.num_steps = num_steps

        # Number of simulations to run
        self.num_batches = num_batches

        # Store results from each simulation
        self.results_from_sim = [0 for i in range(num_batches)]

        # Flag for building animations from the first simulation
        # I'm putting this because the first simulation slows down exponentially with number of steps... bad for quick testing
        self.do_animation = do_animation
        self.animation_moving_average_coefficient = animation_moving_average_coefficient

    def summary(self):
        """Summarises simulation data after a batch run
        """
        # FIXME implement
        print("Summary Time")
        # Total Crimes
        fig = plt.figure()
        crimes = [sim_results.total_crimes_at_step[-1] for sim_results in self.results_from_sim]
        plt.hist(crimes)
        plt.title("Total Crimes")
        plt.show()

        crimes_per_step_per_sim = [sim_results.total_crimes_at_step for sim_results in self.results_from_sim]
        crimes_per_step_per_sim = [sum(x) for x in zip(*crimes_per_step_per_sim)]
        crimes_per_step_per_sim = list(map(lambda x: x / self.num_batches, crimes_per_step_per_sim))
        plt.plot(crimes_per_step_per_sim)
        plt.ylabel("Average Number of Cumulative Crimes")
        plt.xlabel("Step Number")
        plt.title("Average Cumulative Crimes over Simulation Time")
        plt.show()

        ### aggregate and normalize location data ###

        # crime location data
        list_crime_locations = [sim_results.crime_loc for sim_results in self.results_from_sim]
        agg_crime_locations = normalize(
            [sum(x) for x in zip(*list_crime_locations)]
        )

        # civilian location data
        list_civilian_locations = [sim_results.civ_loc for sim_results in self.results_from_sim]
        agg_civilian_locations = normalize(
            [sum(x) for x in zip(*list_civilian_locations)]
        )

        # police location data
        list_police_locations = [sim_results.police_loc for sim_results in self.results_from_sim]
        agg_police_locations = normalize(
            [sum(x) for x in zip(*list_police_locations)]
        )

        # criminal location data
        list_criminal_locations = [sim_results.criminal_loc for sim_results in self.results_from_sim]
        agg_criminal_locations = normalize(
            [sum(cell) for cell in zip(*list_criminal_locations)]
        )

        fig, ax = plt.subplots()
        im = ax.imshow(agg_crime_locations, cmap=plt.get_cmap('plasma'),
                       vmin=0, vmax=1)
        fig.colorbar(im)
        plt.title("Crime Locations")
        ax.invert_yaxis()
        plt.show()

        fig, ax = plt.subplots()
        im = ax.imshow(agg_civilian_locations, cmap=plt.get_cmap('plasma'),
                       vmin=0, vmax=1)
        fig.colorbar(im)
        plt.title("Civilian Locations")
        ax.invert_yaxis()
        plt.show()

        fig, ax = plt.subplots()
        im = ax.imshow(agg_criminal_locations, cmap=plt.get_cmap('plasma'),
                       vmin=0, vmax=1)
        fig.colorbar(im)
        plt.title("Criminal Locations")
        ax.invert_yaxis()
        plt.show()

        fig, ax = plt.subplots()
        im = ax.imshow(agg_police_locations, cmap=plt.get_cmap('plasma'),
                       vmin=0, vmax=1)
        fig.colorbar(im)
        plt.title("Police Locations")
        ax.invert_yaxis()
        plt.show()

        # ------ Animate heatmaps from first simulation -----

        if not self.do_animation:
            return

        # TESTING - Create all animations in one figure
        print("Creating animations...")

        fig, (axCiv, axCrim, axPol) = plt.subplots(1, 3, sharey=True)
        axCiv.set(xlim=(0, self.results_from_sim[0].env.grid_width), ylim=(0, self.results_from_sim[0].env.grid_height))
        axCrim.set(xlim=(0, self.results_from_sim[0].env.grid_width), ylim=(0, self.results_from_sim[0].env.grid_height))
        axPol.set(xlim=(0, self.results_from_sim[0].env.grid_width), ylim=(0, self.results_from_sim[0].env.grid_height))

        def animate(i):
            axCiv.clear()
            axCrim.clear()
            axPol.clear()

            axCiv.set_title("Civilians")
            axCrim.set_title("Criminals")
            axPol.set_title("Police")

            axCiv.imshow(self.results_from_sim[0].civ_heat_maps[i], cmap='plasma', vmin=0, vmax=1)
            axPol.imshow(self.results_from_sim[0].police_heat_maps[i], cmap='plasma', vmin=0, vmax=1)
            axCrim.imshow(self.results_from_sim[0].criminal_heat_maps[i], cmap='plasma', vmin=0, vmax=1)

            axCrim.set_xlabel("Step %s" % str(i))
            axCiv.invert_yaxis()

        anim = animation.FuncAnimation(fig, animate, interval=50, frames=self.num_steps, repeat_delay=1000)
        plt.title("Simulation 0")

        # from https://stackoverflow.com/questions/13784201/matplotlib-2-subplots-1-colorbar
        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
        fig.colorbar(im, cax=cbar_ax)

        anim.save("animations/all_together_heatmap.mp4", writer='ffmpeg')
        plt.draw()
        plt.show()

        return


    def start(self):
        """Begins the batch run, then runs summary statistics
        """
        for batch_number in range(self.num_batches):
            print("Starting simulation number %s" % str(batch_number))
            grid = env.Environment(uid=batch_number)
            grid.populate()

            do_animation = (batch_number == 0 and self.do_animation) # Only doanimation on first simulation
            if do_animation:
                print("WARNING: Creating animation for simulation %s. Delay increases exponentially with # of steps." % str(batch_number))

            dm = dataManager(env=grid,
                             num_runs=self.num_steps,
                             do_animation=do_animation,
                             animation_moving_average_coefficient=self.animation_moving_average_coefficient)
            dm.collect_init_state()

            for step_number in range(self.num_steps):
                grid.tick()
                dm.collect_step_data(step_number)

            # After sim, store results
            self.results_from_sim[batch_number] = dm

        # After batch run, summarise
        self.summary()


class dataManager(object):
    """
    Collects data from a single simulation and processes it.
    """

    # FIXME Add support to include/drop desired data

    def __init__(self, env, num_runs, animation_moving_average_coefficient, do_animation=False):
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
