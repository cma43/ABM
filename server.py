from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import UserSettableParameter

from config.portrayal import *
from Model.sd_env import SDGrid


# Make a world that is 50x50, on a 500x500 display.
canvas_element = CanvasGrid(portrayPDAgent, 50, 50, 500, 500)

#FIXME: This does not let us adjust all the parameters listed when the simulation runs
model_params = {
    "height": 50,
    "width": 50,
    "schedule_type": UserSettableParameter("choice", "Scheduler type", value="Random",
                                           choices=list(SDGrid.schedule_types.keys()))
}

server = ModularServer(SDGrid, [canvas_element], "Social Dilemma",
                       model_params)

                       