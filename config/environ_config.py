#!user/bin/env python3
'''
Configuration file for environmental parameters
Load when instantiating environment variable
'''

environ = {
    'num_criminals':      50,  # number of criminals
    'num_civilians':      100,
    'num_police':         10,
    'resources_init_max_for_criminal': 25,
    'resources_init_max_for_civilian': 50,
    'crime_propensity_init_max': 25,
    'crime_distance':     1,
    'agent_vision_limit': 2,   # Number of cells an agent can see around itself in a grid
    'grid_width':         50,  # Width of grid in number of cells
    'grid_height':        50,  # Height of grid in number of cells
    'crime_propensity_threshold': 1  # The propensity required to commit crimes or be a solo criminal
}
