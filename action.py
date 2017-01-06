#!/usr/bin/env python
#coding=utf-8

'''
Definition of Action class. In AMREAGER, an action can be either 'shift', 'reduce', 'rarc'
or 'larc'. When it's a shift, the argument is the subgraph triggered by the token. When it's a reduce,
the argument is used to specify the optional reeentrant edge to create. For rarcs and rarcs, the
argument is the label for those edges.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

class Action:
    def __init__(self, name, argv = None):
        assert (name == "shift" or name == "larc" or name == "rarc" or name == "reduce")
        self.name = name
        self.argv = argv

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.name, self.argv)

    def __eq__(self, other):
        return self.name == other.name and self.argv == other.argv

    def get_id(self):
        act_id = 0
        if self.name == "shift":
            act_id = 1
        elif self.name == "reduce":
            act_id = 2
        elif self.name == "larc":
            act_id = 3
        elif self.name == "rarc":
            act_id = 4
        return act_id
