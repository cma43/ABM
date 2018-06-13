"""The server.py controls macro parameters for simulations. Including data collection for each episode, etc."""

from Base.batch import batchManager

num_steps = 200
num_episodes = 100

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



