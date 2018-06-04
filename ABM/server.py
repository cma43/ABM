"""The server.py controls macro parameters for simulations. Including data collection for each episode, etc."""

from ABM.batch import batchManager

# FIXME Average Cumulative Crimes and Arrests on Step N graph and 
# Total Number of Coalitions Over Time In First Sim graph when num_steps=1
# and num_episodes = 100 don't display anything, so should have logic to 
# ensure that they're shown only when they're computable.

# FIXME Average Criminal Location and Average Police Location 
# converge to and stay at about the point (5,5) for any simulation.

num_steps = 100
num_episodes = 10

# TODO A feature we should add

data_to_collect = {
    'resources',
    'memory',
    'propensity',
    'network',
    'etc'
}

print("Starting server.")

bm = batchManager(num_episodes=num_episodes,
                  num_steps=num_steps)


bm.start()



