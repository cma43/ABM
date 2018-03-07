import environment as env
import matplotlib.pyplot as plt
import numpy as np

from agent_cma_zl import Agent

# This is what i've been using to practice demo


grid = env.Environment(uid=1)
print(grid.config)

num_runs = 100
police_loc = np.zeros((grid.config['grid_width'] + 1, grid.config['grid_height'] + 1))
single_loc = np.zeros((grid.config['grid_width'] + 1, grid.config['grid_height'] + 1))
civ_loc = np.zeros((grid.config['grid_width'] + 1, grid.config['grid_height'] + 1))
criminal_loc = np.zeros((grid.config['grid_width'] + 1, grid.config['grid_height'] + 1))
crime_loc = np.zeros((grid.config['grid_width'] + 1, grid.config['grid_height'] + 1))
civilian_times_robbed = np.zeros((grid.config['num_civilians']))
civilian_memory_length = np.zeros((grid.config['num_civilians']))
total_crimes_at_step = np.zeros(num_runs)

grid.populate()

# Initialization data collection
init_criminal_location = np.zeros((grid.config['grid_width'] + 1, grid.config['grid_height'] + 1))
for criminal in grid.criminals:
    init_criminal_location[criminal.x][criminal.y] += 1

init_civilian_location = np.zeros((grid.config['grid_width'] + 1, grid.config['grid_height'] + 1))
for civilian in grid.civilians:
    init_civilian_location[civilian.x][civilian.y] += 1
    
init_police_location = np.zeros((grid.config['grid_width'] + 1, grid.config['grid_height'] + 1))
for police in grid.police:
    init_police_location[police.x][police.y] += 1

for i in range(num_runs):
    #grid.update_grid(i)
    grid.tick()

    # Collect Data for this turn
    for police in grid.police:
        police_loc[police.x][police.y] += 1

    for civ in grid.civilians:
        civ_loc[civ.x][civ.y] += 1
        #civilian_times_robbed[civ.uid]

    single_loc[grid.civilians[0].x][grid.civilians[0].y] += 1

    for criminal in grid.criminals:
        criminal_loc[criminal.x][criminal.y] += 1

    for location in grid.crimes_this_turn:
        crime_loc[location[0]][location[1]] += 1
    print(i)

    if i > 0:
        total_crimes_at_step[i] = total_crimes_at_step[i-1] + len(grid.crimes_this_turn)
    else:
        total_crimes_at_step[0] = len(grid.crimes_this_turn)
print("Done")
grid.update_grid(num_runs)

# Post data collection
for civilian in grid.civilians:
    civilian_times_robbed[civilian.uid] = civilian.num_times_robbed
    civilian_memory_length[civilian.uid] = len(civilian.memory)

plt.title("Times robbed vs. Criminals remembered")
ax = plt.subplot()
plt.ylabel("Number of times Robbed")
plt.xlabel("Number of Unique Robbers")
for civilian in grid.civilians:
    ax.scatter(civilian_memory_length[civilian.uid], civilian_times_robbed[civilian.uid], alpha=0.1, c='black')
plt.show()

plt.title("Cumulative Crimes over Time")
ax = plt.subplot()
plt.ylabel("Number of Crimes")
plt.xlabel("Time in steps")
for i in range(num_runs):
    ax.scatter(i, total_crimes_at_step[i], alpha=0.1, c='black')
plt.show()

# Criminal Locations - Init/Average
#https://matplotlib.org/examples/pylab_examples/subplots_demo.html#pylab-examples-subplots-demo
f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)
ax1.imshow(init_criminal_location, cmap='hot', aspect='auto')
ax1.set_title("Initial Criminal Locations")
ax2.imshow(criminal_loc, cmap='hot', aspect='auto')
ax2.set_title("Average Criminal Locations")
ax3.imshow(crime_loc, cmap='hot', aspect='auto')
ax3.set_title("Crime Locations")
ax1.invert_yaxis()
ax1.set_aspect(1)
plt.show()

# Civilian location heat map
f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)
ax1.imshow(init_civilian_location, cmap='hot', aspect='auto')
ax1.set_title("Initial Civilian Locations")
ax2.imshow(civ_loc, cmap='hot', aspect='auto')
ax2.set_title("Average Civilian Locations")
ax3.imshow(crime_loc, cmap='hot', aspect='auto')
ax3.set_title("Crime Locations")
ax1.invert_yaxis()
ax1.set_aspect(1)
plt.show()

# Police information heatmaps
f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)
ax1.imshow(init_police_location, cmap='hot', aspect='auto')
ax1.set_title("Initial Police Locations")
ax2.imshow(police_loc, cmap='hot', aspect='auto')
ax2.set_title("Average Police Locations")
ax3.imshow(crime_loc, cmap='hot', aspect='auto')
ax3.set_title("Crime Locations")
ax1.invert_yaxis()
ax1.set_aspect(1)
plt.show()


# Resource Evaluation
civ_wealth = [x.resources[0] for x in grid.civilians]
plt.hist(civ_wealth)
plt.title("All Civilian Wealth")
plt.show()

# Criminal Wealth
crim_wealth = [x.resources[0] for x in grid.criminals]
plt.hist(crim_wealth)
plt.title("All Criminal Wealth")
plt.show()
