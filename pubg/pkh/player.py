import json

class Player:

    # Constructor
    def __init__(self, name):
        # player name (string)
        self.name = name
        # list of players
        self.victims = []
        # parent (can only have one parent)
        self.parent = None

    # append victim to this player
    def appendVictim(self, victimObject):
        self.victims.append(victimObject)
        victimObject.parent = self

    def hasVictim(self) :
        return len(self.victims) > 0

    def isRoot(self) :
        return self.parent == None

    # check equality by checking name attribute
    def __eq__(self, other):
        return self.name == other

    # debugging
    def __str__(self) :
        toRet = "killer: " + self.name + " victim: "
        for victim in self.victims :
            toRet += victim.name + ", "
        return toRet
