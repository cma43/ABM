def portrayPDAgent(agent):
    '''
    This function is registered with the visualization server to be called
    each tick to indicate how to draw the agent in its current state.
    :param agent:  the agent in the simulation
    :return: the portrayal dictionary
    '''
    
    return {
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "Filled": "true",
        "Layer": 0,
        "x": agent.pos[0],
        "y": agent.pos[1],
        "Color": determine_grid_color(agent)
    }

def determine_grid_color(agent):

    '''
    This function is a helper function to produce correct colors in the 
    social dilemma sim, depending on if it's the Epstein or MESA implementation
    :param agent: agent in simulation
    :return: colors to be used per agent 
    '''
    if agent is None: 
        return "white"
    if agent.move == "C":
        return "blue"
    else:
        return "red"
    