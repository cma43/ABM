"""The server.py controls macro parameters for simulations. Including data collection for each episode, etc."""

from Base.batch import batchManager
import logging

logging.basicConfig(level=logging.INFO, filename='ABM.log')


num_steps = 10
num_episodes = 2

data_to_collect = {
    # Individual, Role, and Custom Group Data Collecting
    # Each should be a list of specifications
    "individuals": [
        # Add a dictionary for each individual/attribute to monitor
        {
            "uid": None,         # None defaults to UID 0
            "role": "civilians",          # civilians/police/criminals
            "attribute": "resources",   # MUST BE SPECIFIED
            "frequency": "step",  # step/episodic
        }
    ],

    "roles": [
        # Collect the attributes for all agents within the specified role
        # Add more dictionaries to collect other agent roles or attributes
        {
            "role": "civilians",
            "attribute": "pos",
            "frequency": "step"
        },
        {
            "role": "criminals",     # Role, as a string
            "attribute": "utility",  # Attribute, as a string
            "frequency": "step"  # "step" or "episodic"
        },
        {
            "role": "residences",     # Role, as a string
            "attribute": "attractiveness",  # Attribute, as a string
            "frequency": "step"  # "step" or "episodic"
        }
    ],

    "groups": [
        # Only agents matching these qualifiers, in this order, will have the specified attribute recorded
        # Leave as None to NOT exclude agents based on that criteria
        {
            "role_qualifier_list": None,  # List of roles as strings, None = ALL roles
            "uid__qualifier_list": None,  # List of uid's as integers, None = ALL agents
            "attribute_qualifier_list": [
                # Add as many qualifiers as desired!
                # None = No attribute qualifiers
                {
                    "attribute": "network",    # Attribute to look for as string
                    "value_list": [0]  # Values the attribute can take on
                }
            ],
            "attribute": "network",  # attribute to be collected
            "frequency": "step"  # step or episodic
        }
    ]
}

print("Starting server.")

bm = batchManager(num_episodes=num_episodes,
                  num_steps=num_steps,
                  data_to_collect=data_to_collect)


bm.start()

# All Data lies in  a list of [data_lists['individuals'/'groups'/'types'][specification_index]['data']]



