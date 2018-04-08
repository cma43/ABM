#!user/bin/env python3
'''
Configuration file for environmental parameters
Load when instantiating environment variable
'''

environ = {
    'num_criminals':      30,  # number of criminals
    'num_civilians':      100,
    'num_police':         30,
    'resources_init_max_for_criminal': 25,
    'resources_init_max_for_civilian': 100,
    'crime_propensity_init_max': 25,
    'crime_distance':     0,
    'agent_vision_limit': 1,   # Number of cells an agent can see around itself in a grid
    'grid_width':         50,  # Width of grid in number of cells
    'grid_height':        50,  # Height of grid in number of cells
    'crime_propensity_threshold': 20,  # The propensity required to commit crimes or be a solo criminal
    'police_dispatch': 'closest',  # 'random'/'closest' behavior for dispatching police to crime scenes
    'civilian_vision_radius': 1,
    'police_vision_radius': 1,
    'police_arrest_probability': 0.2,
    'lambda': 0.05 # mean of criminals entering the grid per second
}
