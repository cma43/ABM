#!user/bin/env python3
'''
Configuration file for environmental parameters
Load when instantiating environment variable
'''

environ = {
    'num_criminals':      10,  # number of criminals
    'num_civilians':      50,
    'num_police':         25,
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
    'criminal_vision_radius': 1, #Radius for criminal vision
    'police_arrest_probability': 1,
    'police_dept_start': 'random', # 'Random/Default' Choose whether to randomly place a PoliceDepartment object or specify it 
    'effective_police_radius': 20,
    'arrest_behavior': 'imprison',  # 'remove' or 'imprison' the criminal when they are arrested
    'lambda': 5,  # avg number of criminals entering the simulation per step, when arrest beahavior is 'remove'
    'maximum_sentence': 20,  # if arrest_behavior is imprison, the max length of time to imprison a criminal
    'coalition_merge_distance': 0,
    'crime_success_probability': 0.8,
    'alpha': 1,  #Shape parameter for Weibull recidivism function, based on https://link.springer.com/content/pdf/10.1007/BF02221141.pdf
    'eta': .02, #Failure rate parameter for Weibull recidivism function, based on https://link.springer.com/content/pdf/10.1007/BF02221141.pdf
    'gamma': .5, #Parameter for probability of becoming permanently a criminal;
    'beta': .5, #Recidivism threshold: if above, then relapse into crime; if below, become civilian
    'travel_penalty': 2,  #The penalty associated with a criminal traveling farther from their home base, or a civilian into dangerous areas
    'kappa': .8,         # discount parameter for computing total utility: 1 means perfectly future oriented and 0 means perfectly present oriented      
    'police_arrest_radius': 1,

    'walk_across_buildings': ['Criminal'] #This is only for criminals and civilians. We assume police can walk across buildings all the time.                 
}