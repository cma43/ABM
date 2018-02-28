import environment as env

from agent_cma_zl import Agent

# This is what i've been using to practice demo

grid = env.Environment(uid=1)
print(0, grid.config)

grid.populate()

for i in range(5):
    grid.update_grid(i)
    grid.tick()