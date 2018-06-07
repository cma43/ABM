"""The server.py controls macro parameters for simulations. Including data collection for each episode, etc."""

from ABM.batch import batchManager

num_steps = 10
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



