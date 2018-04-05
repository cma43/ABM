#!user/bin/env python3
'''
Configuration file for environmental parameters
Load when instantiating environment variable
'''

environ = {
    'num_criminals':      10,  # number of criminals
    'num_civilians':      20,
    'num_police':         1,
    'initial_resource_max': 100,
    'initial_crime_propensity_max': 25,
    'crime_distance':     0,
    'agent_vision_limit': 1,   # Number of cells an agent can see around itself in a grid
    'grid_width':         5,  # Width of grid in number of cells
    'grid_height':        5,  # Height of grid in number of cells
    'crime_propensity_threshold': 0,  # The propensity required to commit crimes or be a solo criminal
    'police_dispatch': 'closest',  # 'random'/'closest' behavior for dispatching police to crime scenes
    'civilian_vision_radius': 1,
    'police_vision_radius': 1,
    'police_arrest_probability': 0.5,
    'effective_police_radius': 5
}
