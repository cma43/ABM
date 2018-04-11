#!user/bin/env python3
'''
Configuration file for environmental parameters
Load when instantiating environment variable
'''

environ = {
    'num_criminals':      10,  # number of criminals
    'num_civilians':      1,
    'num_police':         0,
    'initial_resource_max': 100,
    'initial_crime_propensity_max': 4,
    'crime_distance':     0,
    'agent_vision_limit': 2,   # Number of cells an agent can see around itself in a grid
    'grid_width':         5,  # Width of grid in number of cells
    'grid_height':        5,  # Height of grid in number of cells
    'crime_propensity_threshold': 5,  # The propensity required to commit crimes or be a solo criminal
    'police_dispatch': 'closest',  # 'random'/'closest' behavior for dispatching police to crime scenes
    'civilian_vision_radius': 1,
    'police_vision_radius': 1,
    'police_arrest_probability': 0.5,
    'effective_police_radius': 5,
    'arrest_behavior': 'remove',  # 'remove' or 'imprison' the criminal when they are arrested
    'lambda': 0.05,  # Mean number of criminals entering the simulation per step
    'minimum_sentence': 20,  # if arrest_behavior is imprison, the max length of time to imprison a criminal
    'coalition_merge_distance': 0
}
