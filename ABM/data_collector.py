import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class DataManager(object):
    """Handles the functions for collecting episodic information and for summarizing it."""

    def __init__(self, num_episodes, num_steps, data_to_collect):
        self.num_episodes = num_episodes
        self.num_steps = num_steps

        # Guide for data to collect
        self.data_to_collect = data_to_collect

        # List of data collected
        self.data_in_sim = list()

    def start_new_episode(self, environment):
        """Creates a new dataSim object that will collect information from the specified environment."""
        self.data_in_sim.append(DataSim(environment, self.num_steps, self.data_to_collect))

    def collect_state(self, step_number):
        """Collect specified state data.

        FIXME for now, collect specific data for RAT
        """
        self.data_in_sim[-1].collect_state_data(step_number)
    

class DataSim(object):
    """
    Collects data from a single simulation.
    """

    # TODO Add support to include/drop desired data

    def __init__(self, environment, num_steps, data_to_collect):
        # The environment to get data from
        self.environment = environment

        # The number of steps the simulation is being run for
        self.num_steps = num_steps

        # Instantiate data structures to be used
        self.data_to_collect = data_to_collect
        self._init_data_collection(data_to_collect)



    def _init_data_collection(self, data_to_collect):
        """Instantiates the data structures used to collect the specified data

        Agent references and the collected data are stored in their corresponding specification, as 'agent(s)' and
        'data', respectively.

        Individuals get an array for step-wise collection, a single number for episodic data.
        Roles and Groups store data as a list, each element corresponding to an agent. Step wise data is stored as a list
        within this "master list" for each agent, each element being a step in the episode.
        """

        for specification in self.data_to_collect['individuals']:
            # Instantiate data collection specifications for named individuals

            # Attribute to record MUST BE SPECIFIED
            if "attribute" not in specification or specification['attribute'] is None:
                raise ValueError("Attribute is a required non-null parameter for data collection,"
                                 " please provide a valid agent attribute")

            # Make reference to agent for easy look up later
            print(self.environment.agents[specification['role']][getattr(specification, "uid", 0)])
            specification['agent'] = self.environment.agents[specification['role']][getattr(specification, "uid", 0)]

            if specification['frequency'] == "step":
                # Add an empty list, each step in episode will add an element to this list
                specification['data'] = list()
            if specification['frequency'] == "episodic":
                # Add a place holder zero
                specification['data'] = 0



        # Instantiate data collection specifications for all agents of a certain role
        for specification in self.data_to_collect['roles']:

            # Attribute to record must be specified
            if "attribute" not in specification or specification['attribute'] is None:
                raise ValueError("Attribute is a required non-null parameter for data collection,"
                                 " please provide a valid agent attribute")

            # Role must be specified
            if "role" not in specification or specification['role'] is None:
                raise ValueError("Role is a required non-null parameter for data collection,"
                                 " please provide a valid agent role")

            if specification['role'] not in self.environment.agents.keys():
                raise KeyError("The specified role {0} does not exist in the environment."
                               " Make sure there is a corresponding key in the environment 'agents'"
                               " dictionary.".format(specification['role']))

            # Master data list - each element is an agent reference from the environment role list
            specification['agents'] = list()
            specification['agents'] += self.environment.agents[specification['role']]

            # instantiate data structures
            if specification['frequency'] == "step":
                # Place hold empty lists to contain future data
                specification['data'] = [list() for agent in specification['agents']]
            elif specification['frequency'] == "episodic":
                # Place hold future data with a 0
                specification['data'] = [0 for agent in specification['agents']]

        for specification in self.data_to_collect['groups']:
            # Instantiate data collection specifications for all agents part of a specified group
            # Order of Operations:
            # Role -> UID -> Attributes

            # Attribute must be specified
            if "attribute" not in specification or specification['attribute'] is None:
                raise ValueError("Attribute is a required non-null parameter for data collection,"
                                 " please provide a valid agent attribute")

            # Include all roles if none are specified
            if specification['role_qualifier_list'] is None:
                specification['role_qualifier_list'] = self.environment.agents.keys()

            # Add agent reference for each qualifying agent
            specification['agents'] = list()
            for role in specification['role_qualifier_list']:
                # Only qualifying agents in specified roles will be selected

                for agent in self.environment.agents[role]:
                    if 'uid_qualifier_list' not in specification or \
                            specification['uid_qualifier_list'] is None or\
                            agent.uid in specification['uid_qualifier_list']:
                        # Match agents with matching uid's or all if UID qualifier is not specified

                        if specification['attribute_qualifier_list'] is None:
                            # Add agent if no attribute qualifiers specified by user
                            specification['agents'].append(agent)
                        else:
                            # Must match attribute qualifiers specified by user
                            for attribute_specification in specification['attribute_qualifier_list']:
                                # There can be multiple attributes to match on, confirm each
                                if getattr(agent, attribute_specification['attribute'], None) not in attribute_specification['value_list']:
                                    # Do NOT add agent to reference list, their attributes did not meet the required values
                                    break
                            else:
                                # All attributes matched, add agent to reference loop
                                specification['agents'].append(agent)

            # Now with agents in reference list, we can instantiate the data structures for each
            specification['data'] = list()

            for agent in specification['agents']:
                if specification['frequency'] == "step":
                    # Add empty lists for each agent, each element will be data for the corresponding step
                    specification['data'].append(list())
                if specification['frequency'] == "episodic":
                    # Place hold data with a zero
                    specification['data'].append(0)





    def collect_state_data(self, step_number):
        """
        Collect and store the current data from the environement state.

        FIXME collect specified data points with kwargs

        """

        # TODO make agent lists dictionaries with uid:agent key-value pairs for fast lookup
        # Collect individual step-wise data
        for specification in self.data_to_collect['individuals']:
            # Each specification denotes one user
            if specification['frequency'] == "step":
                # Collect attribute data
                specification['data'].append(getattr(specification['agent'], specification['attribute']))

            elif specification['frequency'] == "episodic" and step_number == self.num_steps:
                # Collect only if last step
                specification['data'].append(getattr(specification['agents'], specification['attribute']))

        # Collect data for Roles
        for specification in self.data_to_collect['roles']:
            if specification['frequency'] == "step":
                for agent_num in range(len(specification['agents'])):
                    # Collect info for each agent in role
                    specification['data'][agent_num].append(getattr(specification['agents'][agent_num],
                                                                    specification['attribute']))

            elif specification['frequency'] == 'episodic' and step_number == self.num_steps:
                for agent_num in range(len(specification['agents'])):
                    # Collect info for each agent in role
                    specification['data'][agent_num].append(getattr(specification['agents'][agent_num],
                                                                     specification['attribute']))

        # Collect data for groups
        for specification in self.data_to_collect['groups']:
            if specification['frequency'] == "step":
                # Agents are predefined in specification during `_init_data_collection`

                for agent_num in range(len(specification['agents'])):
                    # Collect info for each agent
                    specification['data'][agent_num].append(getattr(specification['agents'][agent_num], specification['attribute']))

            elif specification['frequency'] == "episodic" and step_number == self.num_steps:
                # Agents are predefined in spec during `init_data_collection`
                for agent_num in range(len(specification['agents'])):
                    # Collect info for each agent
                    specification['data'][agent_num].append(getattr(specification['agents'][agent_num], specification['attribute']))



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
