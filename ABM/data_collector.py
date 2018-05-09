import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class DataManager(object):
    """Handles the functions for collecting episodic information and for summarizing it."""

    def __init__(self, num_episodes, num_steps):
        self.num_episodes = num_episodes
        self.num_steps = num_steps

        self.data_in_sim = list()

    def start_new_episode(self, environment):
        """Creates a new dataSim object that will collect information from the specified environment."""
        self.data_in_sim.append(DataSim(environment, self.num_steps))

    def collect_state(self, step_number, *args, **kwargs):
        """Collect specified state data.

        FIXME for now, collect specific data for RAT
        """
        self.data_in_sim[-1].collect_state_data(step_number)


class DataSim(object):
    """
    Collects data from a single simulation.
    """

    # TODO Add support to include/drop desired data

    def __init__(self, environment, num_steps):
        # The environment to get data from
        self.environment = environment

        # The number of steps the simulation is being run for
        self.num_steps = num_steps

        # ---------- new data collection format! ------------
        # Location of each agent -- one list of [position1(x,y), position2, ...] for each agent for each step
        self.police_location_at_step = [list() for i in range(self.environment.config['num_police'])]
        self.civilian_location_at_step = [list() for i in range(self.environment.config['num_civilians'])]
        self.criminal_location_at_step = [list() for i in range(self.environment.config['num_criminals'])]

        self.police_location_df = pd.DataFrame

        self.criminal_affiliation = [list() for i in range(self.environment.config['num_criminals'])]

        self.crimes_per_step = [0]
        self.arrests_per_step = [0]
        self.total_coalitions = [0]

    def collect_state_data(self, step_number, **kwargs):
        """
        Collect and store the current data from the environement state.

        FIXME collect specified data points with kwargs

        """

        for attribute in kwargs:
            # Collect data for that attribute....
            # FIXME do this
            pass

        # Collect Location Data for Police, Civilians, Criminals, and Crimes this turn

        # Police
        for police in self.environment.agents['police']:
            self.police_location_at_step[police.uid].append(police.pos)

        for civilian in self.environment.agents['civilians']:
            self.civilian_location_at_step[civilian.uid].append(civilian.pos)

        for criminal in self.environment.agents['criminals']:
            self.criminal_location_at_step[criminal.uid].append(criminal.pos)
            self.criminal_affiliation[criminal.uid].append(criminal.network)

        if step_number == 0:
            self.crimes_per_step[0] = self.environment.total_crimes
            self.arrests_per_step[0] = self.environment.total_arrests
            self.total_coalitions[0] = self.environment.total_coalitions
        else:
            self.crimes_per_step.append(self.environment.total_crimes)
            self.arrests_per_step.append(self.environment.total_arrests)
            self.total_coalitions.append(self.environment.total_coalitions)


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


def normalized_average(individual_locations_per_step, width, height):
    """Takes a list of individual locations per step, aggregates them per step, and scales it from 0 to 1.      """
    
    avg = np.zeros((width, height))

    for individual in individual_locations_per_step:
        for position in individual:
            avg[position[0]][position[1]] += 1

    return normalize(avg)

def average_states(list_of_states, width, height):
    """Takes a list of 2d vectors representing a grid with values on it, averages them, and returns it normalized"""
    avg = np.zeros((width, height))

    for state in list_of_states:
        avg = np.add(avg, state)

    return normalize(avg)
