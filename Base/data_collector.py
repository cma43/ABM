import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



class DataManager(object):
    """Handles the functions for collecting episodic information and for summarizing it."""

    def __init__(self, num_episodes, num_steps, data_to_collect):
        self.num_episodes = num_episodes
        self.num_steps = num_steps

        # Specifications for data to collect
        self.data_to_collect = data_to_collect

        # List of data collected, each element contains specifications for one simulation
        self.data_in_sim = list()

        self.environment_size = None  # jerry-rigged variable, collect size of environment in start_new_episode() and put in here

    def start_new_episode(self, environment):
         """Creates a new dataSim object that will collect information from the specified environment."""

         self.environment_size = environment.grid.width, environment.grid.height ## "hack" for collecting grid size
         self.data_in_sim.append(DataSim(environment, self.num_steps, self.data_to_collect))

    def collect_state(self, step_number):
        """Collect specified data at the current step.
        """
        self.data_in_sim[-1].collect_state_data(step_number)

    def get_data(self):
        """Return ALL of the data collected, from each episode.

        A list of specification dictionaries, each element is one episode
        """
        return self.data_in_sim

    def episode_summary(self):
        """Creates generic plots for each completed episode for the specified data

        TODO Heatmaps need to be created/animated when a specification['attribute'] is "pos"
        """
        for specification in self.data_to_collect['individuals']:
            if specification['frequency'] != "step":
                continue
            plt.plot(range(self.num_steps), list(specification['data'][specification['attribute']]))
            plt.title(specification['role'] + " " + str(getattr(specification, 'uid', 0)) + "'s " + specification['attribute'] + " over episode")
            plt.figure(0)
            plt.show() 

        for specification in self.data_to_collect['roles'] + self.data_to_collect['groups']:
            if specification['frequency'] != "step":
                # Ignore episodic data
                continue
            if specification['attribute'] == "pos":
                # FIXME doesn't work because of create_heatmap_from_spec_data()
                # Only do this for position attributes
                continue  ## TODO Remove this when you want to make heat maps
                hm = create_heatmap_from_spec_data(specification, self.environment_size)
                plt.imshow(hm, cmap="Greens", alpha=0.8, extent=(0, self.environment_size[0], 0, self.environment_size[1]))
                plt.figure(3)
                plt.show()
            else:
                l = average_list(specification['data'])
                print("{0}\n{1}\n{2}".format(list(l), len(list(l)), list(l)[0]))
                plt.plot(range(self.num_steps), l)
                plt.title(specification['attribute'] + " average")
                plt.figure(2)
                plt.show()

    def batch_summary(self):
        """Creates generic plots at the end of the batch for the specified data"""
        # TODO implement
        raise NotImplementedError

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

        Agent references and the collected data are stored in their corresponding specification, in key/value pairs
        with 'agent(s)' and 'data', respectively.

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
                # specification['data'] = np.zeros(self.num_steps)
                d = {'step': range(0, self.num_steps), specification['attribute']: np.zeros(self.num_steps)}
                specification['data'] = pd.DataFrame(data=d)
                
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

            # Invalid Role
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
                #if specification['attribute'] == "pos":
                    # TODO from Chris: I had to make this a different data structure b/c np.arrays must have elements of the same length, i.e. we can't replace zeros with tuples (0,0)
                    #specification['data'] = np.empty(self.num_steps, dtype=tuple)
                # specification['data'] = [np.zeros(self.num_steps) for agent in specification['agents']]
                d = {'step': range(0, self.num_steps)}
                for agent in specification['agents']:
                    d[str(agent.uid)] = np.zeros(self.num_steps)
                specification['data'] = pd.DataFrame(d)
            elif specification['frequency'] == "episodic":
                # Place hold future data with a 0
                specification['data'] = [0 for agent in specification['agents']]

        for specification in self.data_to_collect['groups']:
            # Instantiate data collection specifications for all agents part of a specified group, only for agents
            # that meet the specified qualifier criteria

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
            # specification['data'] = list()
            
            if specification['frequency'] == "step":
                d = {'step': range(0, self.num_steps)}
                for agent in specification['agents']:
                    d[str(agent.uid)] = np.zeros(self.num_steps)
                specification['data'] = pd.DataFrame(d)
            elif specification['frequency'] == "episodic":
                # Place hold future data with a 0
                specification['data'] = [0 for agent in specification['agents']]

#            for agent in specification['agents']:
#                # Data structure looks different for step data than it does for episodic data
#                if specification['frequency'] == "step":
#                    # Add empty lists for each agent, each element will be data for the corresponding step
#                    specification['data'].append(np.zeros(self.num_steps))
#                if specification['frequency'] == "episodic":
#                    # Place hold data with a zero
#                    specification['data'].append(0)





    def collect_state_data(self, step_number):
        """
        Collect and store the current data from the environement state.

        FIXME collect specified data points with kwargs

        """

        # Collect individual step-wise data
        for specification in self.data_to_collect['individuals']:
            # Each specification denotes one user
            if specification['frequency'] == "step":
                # Collect attribute data
                attribute = getattr(specification['agent'], specification['attribute'])
                # For attributes that are lists, grab the last recorded/last element in the list
                specification['data'].at[step_number, specification['attribute']] = de_list_attribute(attribute)

            elif specification['frequency'] == "episodic" and step_number == self.num_steps:
                # Collect only if last step
                specification['data'].append(getattr(specification['agents'], specification['attribute']))

        # Collect data for Roles
        for specification in self.data_to_collect['roles']:
            if specification['frequency'] == "step":
                for agent in specification['agents']:
                    # Collect info for each agent in role
                    attribute = de_list_attribute(getattr(agent, specification['attribute']))

                    if specification['attribute'] == "pos":
                        np.append(specification['data'], attribute)
                    else:
                        specification['data'][step_number, str(agent.uid)] = attribute

            elif specification['frequency'] == 'episodic' and step_number == self.num_steps:
                for agent_num in range(len(specification['agents'])):
                    # Collect info for each agent in role
                    specification['data'][agent_num][step_number] = de_list_attribute(getattr(specification['agents'][agent_num],
                                                                     specification['attribute']))

        # Collect data for groups
        for specification in self.data_to_collect['groups']:
            if specification['frequency'] == "step":
                # Agents are predefined in specification during `_init_data_collection`

                for agent in specification['agents']:
                    # Collect info for each agent
                    specification['data'][step_number, str(agent.uid)] = de_list_attribute(getattr(agent, specification['attribute']))

            elif specification['frequency'] == "episodic" and step_number == self.num_steps:
                # Agents are predefined in spec during `init_data_collection`
                for agent_num in range(len(specification['agents'])):
                    # Collect info for each agent
                    specification['data'][agent_num][step_number] = de_list_attribute(getattr(specification['agents'][agent_num], specification['attribute']))

def de_list_attribute(attribute_list):
    """Helper function that takes the last element of nested lists"""
    while type(attribute_list) is list:
        if len(attribute_list) == 0:
            attribute_list = 0  # FIXME this is temp fix for when utility is an empty list, for some reason
            break
        attribute_list = attribute_list[-1]

    return attribute_list

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

def average_list(data_list):
    """Takes a list of lists and averages them element wise"""
    element_count = len(data_list.iloc[:,0])

    final_list = np.zeros(element_count) # place to sum elements

    for i in range(1, len(data_list.iloc[0,:])):
        np.add(final_list, list(data_list.iloc[:,i]), out=final_list)  # sum elements

    np.multiply(final_list, 1/len(data_list.iloc[0,:]-1), out=final_list)  # average

    return final_list

def create_heatmap_from_spec_data(spec, grid):
    """Creates a normalized location heatmap from a specification and a grid, used for size reference"""
    # FIXME I don't think the data is in the correct format for normalized_average()
    assert spec['attribute'] == "pos"

    grid = normalized_average(spec['data'], grid[0], grid[1])
    return grid




















#print(self.environment.agents[specification['role']][getattr(specification, "uid", 0)])
#            specification['agent'] = self.environment.agents[specification['role']][getattr(specification, "uid", 0)]
#
#            if specification['frequency'] == "step":
#                # Add an empty list, each step in episode will add an element to this list
#                specification['data'] = np.zeros(self.num_steps)
#            if specification['frequency'] == "episodic":
#                # Add a place holder zero
#                specification['data'] = 0