# -*- coding: utf-8 -*-
"""

"""

class Coalition(object):
    """Parent class, A group of agents"""

    def __init__(self, uid, environment):
        """A coalition needs it's environment and list of members."""
        self.uid = uid
        self.environment = environment
        self.members = list()

    def merge(self, other_coatlition):
        """Merge another coalition's members into this coalition"""
        raise NotImplementedError

    def remove_member(self, agent):
        """Remove the specified agent from the coalition"""
        for member in self.members:
            if agent is member:
                self.members.remove(agent)
                return

    def add_member(self, agent):
        """Add specified agent to this coalition."""
        raise NotImplementedError

    def remove_coalition(self):
        """Dissolve this coalition."""
        raise NotImplementedError