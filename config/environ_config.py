#!user/bin/env python3
'''
Configuration file for environmental parameters
Load when instantiating environment variable
'''

environ = {
    'num_criminals':      2,  # number of criminals
    'num_civilians':      50,
    'num_police':         10,
    'resources_init_max_for_criminal': 25,
    'resources_init_max_for_civilian': 50,
    'crime_propensity_init_max': 25,
    'agent_vision_limit': 2,   # Number of cells an agent can see around itself in a grid
    'grid_width':         30,  # Width of grid in number of cells
    'grid_height':        30,  # Height of grid in number of cells
    'crime_propensity_threshold': 10  # The propensity required to commit crimes or be a solo criminal
}
