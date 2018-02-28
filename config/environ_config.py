#!user/bin/env python3
'''
Configuration file for environmental parameters
Load when instantiating environment variable
'''

environ = {
    'num_criminals':         50,  # number of criminals
    'num_civilians':      50,
    'num_police':         10,
    'resources_init_max_for_criminal': 5,
    'resources_init_max_for_criminal': 10,
    'crime_propensity_init_max': 25,
    'agent_vision_limit': 3,   # Number of cells an agent can see around itself in a grid
    'grid_width':         10,  # Width of grid in number of cells
    'grid_height':        10,  # Height of grid in number of cells
    'crime_propensity_threshold': 20  # The propensity required to commit crimes or be a solo criminal
}
