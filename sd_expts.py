from Model.sd_env import SDGrid
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.gridspec

model = SDGrid(50, 50, "Random", implement="Epstein")
C=1
D=0
def run_model(model):

    '''
    Run an experiment with a given model, and plot the results.
    '''
    fig = plt.figure(figsize=(12,8))
    
    ax1 = fig.add_subplot(231)
    ax2 = fig.add_subplot(232)
    ax3 = fig.add_subplot(233)
    ax4 = fig.add_subplot(212)
    
    draw_grid(model, ax1)
    model.run(150)
    draw_grid(model, ax2)
    model.run(150)
    draw_grid(model, ax3)
    model.datacollector.get_model_vars_dataframe().plot(kind='bar', ax = ax4, stacked = True)#color = ['b', 'r']) #FIXME: colors correct; plotting seems wrong
    for i, t in enumerate(ax4.get_xticklabels()):
        if (i % 100) != 0:
            t.set_visible(False)
    # model_data = model.datacollector.get_model_vars_dataframe()
    # plt.xticks(np.arange(model_data.shape[0]))
    # plt.hist(model_data, bins= model_data.shape[0], density= True)
    # print(model_data)
    plt.show()


def simulate_model(model, n_eps = 1, simulation_length = [25, 50, 95], to_implement = "IoF"):
    fig = plt.figure(figsize=(12,10))
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    ax = [ax1, ax2, ax3]
  
    for i, e in enumerate(simulation_length):
        sim_data = []
        for _ in range(n_eps):
            model = SDGrid(50,50,"Random", seed= np.random.normal(), implement=to_implement)
            model.run(e)
            #model.datacollector.get_model_vars_dataframe().plot(ax=ax[i])
            sim_data.append(model.datacollector.get_model_vars_dataframe())
    
        plot_to_show = pd.concat(sim_data)
        by_row_index = plot_to_show.groupby(plot_to_show.index)
        plot_to_show_means = by_row_index.mean()
        plot_to_show_means.plot(ax = ax[i])
        #ax[i].get_legend().remove()
        ax[i].set_title("{} Simulation Plot for Average Over {} Episodes of Length T={}".format(model.implement, n_eps, simulation_length[i]))
        ax[i].axhline(1, color = "black", ls = '--')
        ax[i].axhline(0, color = "black", ls = '--')
    
    plt.show()

bwr = plt.get_cmap("bwr")

def draw_grid(model, ax=None):
    '''
    Draw the current state of the grid, with Defecting agents in red
    and Cooperating agents in blue.
    '''
    if not ax:
        fig, ax = plt.subplots(figsize=(6,6))
    grid = np.zeros((model.grid.width, model.grid.height))

    for agent, x, y in model.grid.coord_iter():
    
        if model.implement == "Epstein":
            if agent is None:
                grid[y][x] = 0
            elif agent.move == D:
                grid[y][x] = 1
            elif agent.move == C:
                grid[y][x] = -1

        else:
            if agent.move == D:
                grid[y][x] = 1
            else:
                grid[y][x] = 0
    
    if model.implement == "Epstein":
        ax.pcolormesh(grid, cmap=bwr, vmin=-1, vmax=1)
    else: 
        ax.pcolormesh(grid, cmap = bwr, vmin = 0, vmax=1)
    ax.axis('off')
    ax.set_title("Steps: {}".format(model.schedule.steps))
  


if __name__ == "__main__":

    #models = ["IoF"]
    for _ in range(1):
        run_model(model)
    #for j in range(len(models)):
     #   simulate_model(model, to_implement=models[j])

