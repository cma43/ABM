# -*- coding: utf-8 -*-
"""

"""

class Coalition(object):
    """Parent class, A group of agents"""

    def __init__(self, uid, environment):
        """A coalition needs it's environment and list of members.
        :param uid: The unique id for the coalition.
        :param environment: The environment the coalition is in."""
        self.uid = uid
        self.environment = environment
        self.members = list()

    def merge(self, other_coalition):
        """Merge another coalition's members into this coalition.
        :param other_coalition: Another coalition the coalition will merge with."""
        raise NotImplementedError

    def remove_member(self, agent):
        """Remove the specified agent from the coalition.
        :param agent: The agent that will be removed from the coalition."""
        for member in self.members:
            if agent is member:
                self.members.remove(agent)
                return

    def add_member(self, agent):
        """Add specified agent to this coalition.
        :param: The agent that will be added as a member of the coalition."""
        raise NotImplementedError

    def remove_coalition(self):
        """Dissolve this coalition."""
        raise NotImplementedError