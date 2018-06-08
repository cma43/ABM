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
    'grid_width':         50,  # Width of grid in number of cells
    'grid_height':        50,  # Height of grid in number of cells
    'crime_propensity_threshold': 0,  # The propensity required to commit crimes or be a solo criminal
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
    'crime_success_probability': 0.8,
    'alpha': .5,   #The output elasticity for agent's utility functions/the % change in output per 1% change in all inputs
    'gamma': 0, #Parameter for how agents substitute between inputs using constant elasticity of substitution (CES) utility function;
    'utility_function_type': 'type_2', #Preset utility functions: Type 1 := CES w/ gamma=1 (perfect substitution);
                                      #                          Type 2 := CES w/gamma=negative infinity (No substitution);
                                      #                          Type 3 := CES w/gamma=0 (Unit elasticity of subsitution)
    'travel_penalty': 2,  #The penalty associated with a criminal traveling farther from their home base, or a civilian into dangerous areas
    'kappa': .8,         # discount parameter for computing total utility: 1 means perfectly future oriented and 0 means perfectly present oriented      
    'police_arrest_radius': 1                 
}