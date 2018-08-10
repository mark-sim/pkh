import json

class Jsonutil:
    
    def jsonStartingFromRoot(self, rootPlayers) :
        d = {}
        # PUBG is unique. No players can have the name "PUBG"
        d['name'] = "PUBG"
        d['fake'] = "true"
        if len(rootPlayers) > 0 :
            d['children'] = [self.get_nodes(rootPlayer) for rootPlayer in rootPlayers]
        return d

    def get_nodes(self, node):
        d = {}
        d['name'] = node.name
        children = self.get_children(node)
        if children:
            d['children'] = [self.get_nodes(child) for child in children]
        return d

    def get_children(self, node):
        return node.victims