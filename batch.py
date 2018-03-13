"""
Run a specified number of simulaiton "batches" for a specific number of turns or until a terminal condition has been
reached within the simulation.

FIXME Add support for collecting specified data (e.g. location data, number of crimes) In the future, we may want \
FIXME certain data but not other computationally intensive stuff.

Created: March 9, 2018
Author: Chris Nobblitt
"""

import environment as env
import matplotlib.pyplot as plt
import numpy as np
import copy
from functools import reduce

class batchManager(object):
    """
    Manages batch runs and data collection among runs
    """

    def __init__(self, num_steps, num_batches):
        # Number of steps to run in each simulation
        self.num_steps = num_steps

        # Number of simulations to run
        self.num_batches = num_batches

        # Store results from each simulation
        self.results_from_sim = [0 for i in range(num_batches)]

    def summary(self):
        """Summarises simulation data after a batch run
        """
        # FIXME implement
        print("Summary Time")
        # Total Crimes
        crimes = [sim_results.total_crimes_at_step[-1] for sim_results in self.results_from_sim]
        plt.hist(crimes)
        plt.title("Total Crimes")
        plt.show()

        # Aggregate Crime Location Heatmap
        list_crime_locations = [sim_results.criminal_loc for sim_results in self.results_from_sim]
        agg_crime_locations = [sum(x) for x in zip(*list_crime_locations)]
        plt.title("Aggregate Crime Locations")
        plt.imshow(agg_crime_locations, cmap='hot', aspect='auto')
        plt.show()

        # Aggregate Civilians
        list_civilian_locations = [sim_results.civ_loc for sim_results in self.results_from_sim]
        agg_civilian_locations = [sum(x) for x in zip(*list_civilian_locations)]

        list_init_civilian_locations = [sim_results.init_civilian_loc for sim_results in self.results_from_sim]
        agg_init_civilian_locations = [sum(x) for x in zip(*list_init_civilian_locations)]

        # Civilian location heat map
        f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)
        ax1.imshow(agg_init_civilian_locations, cmap='hot', aspect='auto')
        ax1.set_title("Aggregate Initial Civilian Locations")
        ax2.imshow(agg_civilian_locations, cmap='hot', aspect='auto')
        ax2.set_title("Aggregate Civilian Locations")
        ax3.imshow(agg_crime_locations, cmap='hot', aspect='auto')
        ax3.set_title("Aggregate Crime Locations")
        ax1.invert_yaxis()
        plt.show()

        # Aggregate Police
        list_init_police_locations = [sim_results.init_police_loc for sim_results in self.results_from_sim]
        agg_init_police_locations = [sum(x) for x in zip(*list_init_police_locations)]

        list_police_locations = [sim_results.police_loc for sim_results in self.results_from_sim]
        agg_police_locations = [sum(x) for x in zip(*list_police_locations)]

        # Police information heatmaps
        f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)
        ax1.imshow(agg_init_police_locations, cmap='hot', aspect='auto')
        ax1.set_title("Aggregate Initial Police Locations")
        ax2.imshow(agg_police_locations, cmap='hot', aspect='auto')
        ax2.set_title("Aggregate Police Locations")
        ax3.imshow(agg_crime_locations, cmap='hot', aspect='auto')
        ax3.set_title("Aggregate Crime Locations")
        ax1.invert_yaxis()
        plt.show()

        # Criminal information aggregation
        list_init_criminal_locations = [sim_results.init_criminal_loc for sim_results in self.results_from_sim]
        agg_init_criminal_locations = [sum(cell) for cell in zip(*list_init_criminal_locations)]

        list_criminal_locations = [sim_results.criminal_loc for sim_results in self.results_from_sim]
        agg_criminal_locations = [sum(cell) for cell in zip(*list_criminal_locations)]

        # heatmaps
        f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)
        ax1.imshow(agg_init_criminal_locations, cmap='hot', aspect='auto')
        ax1.set_title("Aggregate Initial Criminal Locations")
        ax2.imshow(agg_criminal_locations, cmap='hot', aspect='auto')
        ax2.set_title("Aggregate Criminal Locations")
        ax3.imshow(agg_crime_locations, cmap='hot', aspect='auto')
        ax3.set_title("Aggregate Crime Locations")
        ax1.invert_yaxis()
        plt.show()




    def start(self):
        for batch_number in range(self.num_batches):
            print("Starting batch number %s" % str(batch_number))
            grid = env.Environment(uid=batch_number)
            grid.populate()

            dm = dataManager(env=grid,num_runs=self.num_steps)
            dm.collect_init_state()

            for step_number in range(self.num_steps):
                grid.tick()
                dm.collect_step_data(step_number)

            # After sim, store results
            self.results_from_sim[batch_number] = copy.deepcopy(dm)

        # After batch run, summarise
        self.summary()


class dataManager(object):
    """
    Collects data from a single simulation and processes it.
    """

    # FIXME Add support to include/drop desired data

    def __init__(self, env, num_runs):
        self.env = env
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
        # Collect Data for this turn
        for police in self.env.police:
            self.police_loc[police.x][police.y] += 1

        for civ in self.env.civilians:
            self.civ_loc[civ.x][civ.y] += 1
            self.civilian_times_robbed[civ.uid]

        self.single_loc[self.env.civilians[0].x][self.env.civilians[0].y] += 1

        for criminal in self.env.criminals:
            self.criminal_loc[criminal.x][criminal.y] += 1

        for location in self.env.crimes_this_turn:
            self.crime_loc[location[0]][location[1]] += 1

        if step_number > 0:
            self.total_crimes_at_step[step_number] = self.total_crimes_at_step[step_number - 1] + len(self.env.crimes_this_turn)
        else:
            self.total_crimes_at_step[0] = len(self.env.crimes_this_turn)
