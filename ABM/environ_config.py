#!user/bin/env python3
'''
Configuration file for environmental parameters
Load when instantiating environment variable
'''

environ = {
    'num_criminals':      20,  # number of criminals
    'num_civilians':      40,
    'num_police':         10,
    'initial_resource_max': 100,
    'initial_crime_propensity_max': 4,
    #'crime_distance':     0,  # TODO currently only does 0, see envrionment.attempt_arrest
    'agent_vision_limit': 3,   # Number of cells an agent can see around itself in a grid
    'grid_width':         10,  # Width of grid in number of cells
    'grid_height':        10,  # Height of grid in number of cells
    'crime_propensity_threshold': 15,  # The propensity required to commit crimes or be a solo criminal
    'police_dispatch': 'closest',  # 'random'/'closest' behavior for dispatching police to crime scenes
    #'civilian_vision_radius': 1,
    #'police_vision_radius': 1,
    'police_arrest_probability': 1,
    'police_dept_start': 'random', # 'Random/Default' Choose whether to randomly place a PoliceDepartment object or specify it 
    'effective_police_radius': 20,
    'arrest_behavior': 'imprison',  # 'remove' or 'imprison' the criminal when they are arrested
    'lambda': 5,  # avg number of criminals entering the simulation per step, when arrest beahavior is 'remove'
    'maximum_sentence': 20,  # if arrest_behavior is imprison, the max length of time to imprison a criminal
    'coalition_merge_distance': 0,
    'crime_success_probability': 0.8
}
