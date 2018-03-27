import environment as env
import matplotlib.pyplot as plt
import numpy as np

from agent_cma_zl import Agent

import matplotlib.animation as animation

# This is what i've been using to practice demo


grid = env.Environment(uid=1)
print(grid.config)

num_runs = 100

grid.populate()

# gif
fig, ax = plt.subplots()
ax.xaxis.set_major_locator(plt.MultipleLocator(1))
ax.xaxis.grid(True, which='major')
ax.yaxis.set_major_locator(plt.MultipleLocator(1))
ax.yaxis.grid(True, which='major')
ax.set_xlim(0, grid.config['grid_width'])
ax.set_ylim(0, grid.config['grid_height'])


def update(i):
    ax.clear()
    ax.xaxis.set_major_locator(plt.MultipleLocator(1))
    ax.xaxis.grid(True, which='major')
    ax.yaxis.set_major_locator(plt.MultipleLocator(1))
    ax.yaxis.grid(True, which='major')
    ax.set_xlim(0, grid.config['grid_width'])
    ax.set_ylim(0, grid.config['grid_height'])
    ax.set_xlabel(i)

    for coalition in grid.coalitions:
        # print("COALITION: " + str(coalition.uid) + " " + str(coalition.x) + ", " + str(coalition.y))
        ax.annotate(str(coalition.uid), (coalition.x, coalition.y))
        for criminal in coalition.members:
            # print(str(criminal.uid) + ": " + str(criminal.x) + ", " + str(criminal.y))
            ax.scatter(criminal.x, criminal.y, color="red", marker='x')

    for civilian in grid.civilians:
        ax.scatter(civilian.x, civilian.y, color="blue")

    for police in grid.police:
        ax.scatter(police.x, police.y, color="black", marker='o')

    grid.tick()

    return ax


if __name__ == '__main__':
    anim = animation.FuncAnimation(fig, update, frames=np.arange(0, num_runs), interval=1)
    plt.show()
    anim.save("rat_animation_normal.html", fps=3)


