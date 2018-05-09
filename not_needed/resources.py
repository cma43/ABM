
# -*- coding: utf-8 -*-
"""

@author: conar
"""

#from agents import Agent
#from network import Network

class Resources():
    
     """ A class for managing and computing resources
    
    Attributes:

        resources: The amount of each asset the agent has
        resource_history: The history of changes for the amount of a resource
        resource_params: Parameters that may guide, change, or influence the 
        evolution of a resource over time
    """
    
     def __init__(self, resources = [], resource_history = [], resource_params = []):
               
        self.resources = resources
        self.resource_history = resource_history
        self.resource_params = resource_params

     def getResource(self):
        #Function for retrieving resource after applying user parameters


        #Return computed resource
        return self.resource 
    
     def tick(self, resource_params):
        #Function for updating resources, if there's a rule for resource
        #evolution
        
        return self.new_resource
        
  