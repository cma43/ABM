"""
Run a specified number of simulation "batches" for a specific number of turns or until a terminal condition has been
reached within the simulation.

FIXME Add support for collecting specified data (e.g. location data, number of crimes) In the future, we may want \
FIXME certain data but not other computationally intensive stuff.

Created: March 9, 2018
Author: Chris Nobblitt
"""

import matplotlib.pyplot as plt
import Base.environment
from Base.data_collector import DataManager, normalized_average, average_states, normalize
import matplotlib.animation as animation


class batchManager(object):
    """
    Manages batch runs and data collection among runs.
    """

    def __init__(self, num_steps, num_episodes, data_to_collect):
        """
        :param num_steps: Number of steps to run in each simulation.
        :param num_episodes: Number of simulations to run.
        :param data_to_collect: The list of types of data to collect.
        """
        # Number of steps to run in each simulation
        self.num_steps = num_steps

        # Number of simulations to run
        self.num_episodes = num_episodes

        self.dm = DataManager(num_steps=self.num_steps,
                              num_episodes=self.num_episodes,
                              data_to_collect=data_to_collect)
    
        self.results = list()

    def start(self):
        """Begins the batch run, then runs summary statistics.
        """
        # TODO Make env consistent across episodes
        
        
        
        
        for batch_number in range(self.num_episodes):
            print("Starting simulation number %s" % str(batch_number))
            new_environment = Base.environment.Environment(uid=batch_number)
            new_environment.populate()
            #new_environment.plot()
            # Begin the new simulation
            self.dm.start_new_episode(new_environment)
  
            for step_number in range(self.num_steps):
                new_environment.tick()
                new_environment.plot(batch_number, step_number)
                self.dm.collect_state(step_number)
                


            self.results += self.dm.get_data()
            #self.dm.episode_summary()

            # results += self.dm.get_data()
            # self.dm.episode_summary()

            # Summarise episodic data
        self.dm.batch_summary
        return self.results
    
    

    def summary(self):
        # FIXME Deprecated - this was for v.01
        """Summarises simulation data after a batch run.
        """
        # FIXME implement

        print("Summary Time")

        # ----- Looking at crimes per step
        # A vector of vectors, for each sim in order
        list_of_crimes_per_step_per_sim = [individual_sim_data.crimes_per_step for individual_sim_data in self.dm.data_in_sim]


        # ----- Looking at arrests per step
        list_of_arrests_per_step_per_sim = [individual_sim_data.arrests_per_step for individual_sim_data in self.dm.data_in_sim]
        
        print(*list_of_arrests_per_step_per_sim, sep='\n')
        
        cumulative_arrests_per_step = [sum(x) for x in zip(*list_of_arrests_per_step_per_sim)]
        cumulative_arrests_per_step = list(map(lambda x: x / self.num_episodes, cumulative_arrests_per_step))

        crimes_per_step_per_sim = [sim_results.crimes_per_step for sim_results in self.dm.data_in_sim]
        crimes_per_step_per_sim = [sum(x) for x in zip(*crimes_per_step_per_sim)]
        crimes_per_step_per_sim = list(map(lambda x: x / self.num_episodes, crimes_per_step_per_sim))

        arrests_per_step_per_sim = [sim_results.arrests_per_step for sim_results in self.dm.data_in_sim]
        arrests_per_step_per_sim = [sum(x) for x in zip(*arrests_per_step_per_sim)]
        arrests_per_step_per_sim = list(map(lambda x: x / self.num_episodes, arrests_per_step_per_sim))
        
        
        # Plot test plots
        fig, ax = plt.subplots()
        ax.plot(arrests_per_step_per_sim, label='Arrests')
        ax.plot(crimes_per_step_per_sim, label='Crimes')
        ax.legend()
        plt.ylabel("Average Number")
        plt.xlabel("Step Number")
        plt.title("Average Cumulative Crimes and Arrests on step n")
        plt.show()
        
        # Total coalitions
        
        # FIXME The current histogram looks like its axes are flipped.
        plt.hist(self.dm.data_in_sim[0].total_coalitions, bins = self.num_steps)
        plt.ylabel("Number of Coalitions")
        plt.xlabel("Step Number")
        plt.title("Total number of coalitions over time in first sim")
        plt.show()

      
        width = self.dm.data_in_sim[0].environment.grid.width
        height = self.dm.data_in_sim[0].environment.grid.height
        extent = 0, self.dm.data_in_sim[0].environment.grid.width, 0, self.dm.data_in_sim[0].environment.grid.height
        fig = plt.figure(frameon=True)


        # Police
        police_avg = []
        for i in range(self.num_episodes):
            police_avg.append(normalized_average(self.dm.data_in_sim[i].police_location_at_step,
                                        width, height))
        police_avg = average_states(police_avg, width, height)
        im1 = plt.imshow(police_avg, cmap="Blues", alpha=0.8, extent=extent)
        plt.title("Average Police Location")
        plt.show()

        # Criminals
        criminal_avg = []
        for i in range(self.num_episodes):
            criminal_avg.append(normalized_average(self.dm.data_in_sim[i].criminal_location_at_step,
                                                 width, height))
        criminal_avg = average_states(criminal_avg, width, height)
        im1 = plt.imshow(criminal_avg, cmap="Reds", alpha=0.8, extent=extent)
        plt.title("Average Criminal Location")
        plt.show()

        # Civilians
        civilian_avg = []
        for i in range(self.num_episodes):
            civilian_avg.append(normalized_average(self.dm.data_in_sim[i].civilian_location_at_step,
                                                 width, height))
        civilian_avg = average_states(civilian_avg, width, height)
        im1 = plt.imshow(civilian_avg, cmap="Greens", alpha=0.8, extent=extent)
        plt.title("Average Civilian Location")
        plt.show()

        # TODO Animation






        return





        #---- old stuff
        # Total Crimes
        fig = plt.figure()
        crimes = [sim_results.total_crimes_at_step[-1] for sim_results in self.results_from_sim]
        plt.hist(crimes)
        plt.title("Total Crimes")
        plt.show()

        crimes_per_step_per_sim = [sim_results.total_crimes_at_step for sim_results in self.results_from_sim]
        crimes_per_step_per_sim = [sum(x) for x in zip(*crimes_per_step_per_sim)]
        crimes_per_step_per_sim = list(map(lambda x: x / self.num_episodes, crimes_per_step_per_sim))
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



