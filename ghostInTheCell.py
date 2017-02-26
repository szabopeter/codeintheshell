import sys
import math

def log(msg):
    # Write an action using print
    print(msg, file=sys.stderr)


class Factory(object):
    def __init__(self, fid, owner, cyborgs, production):
        self.fid = fid
        self.owner, self.cyborgs, self.production = owner, cyborgs, production
        owner = 1 if owner == 1 else -1
        self.current_value = owner * self.cyborgs
        self.score = None
        self.score_as_source = None
        self.accessibility = 1.0

    def markTarget(self, troop):
        self.current_value += troop.owner * troop.cyborgs


class Troop(object):
    def __init__(self, tid, owner, coming_from, going_to, cyborgs, turns_left):
        self.tid = tid
        self.owner, self.cyborgs = owner, cyborgs
        self.coming_from, self.going_to = coming_from, going_to
        self.turns_left = turns_left


class GhostInTheShell(object):
    def __init__(self, factory_count):
        self.factory_count = factory_count
        self.connection = {}

    def connect(self, factid1, factid2, distance):
        if factid1 not in self.connection:
            self.connection[factid1] = {}
        if factid2 not in self.connection:
            self.connection[factid2] = {}
        self.connection[factid1][factid2] = distance
        self.connection[factid2][factid1] = distance

    def turn(self):
        self.factory = {}
        self.troop = {}

    def updateFactory(self, factory_id, owner, cyborgs, production, unused1, unused2):
        self.factory[factory_id] = Factory(factory_id, owner, cyborgs, production)

    def updateTroop(self, troop_id, owner, coming_from, going_to, cyborgs, turns_left):
        self.troop[troop_id] = Troop(troop_id, owner, coming_from, going_to, cyborgs, turns_left)

    def completeUpdate(self):
        for troop in self.troop.values():
            factory = self.factory[troop.going_to]
            factory.markTarget(troop)
        for factory in self.factory.values():
            accval = 0
            for other in self.factory.values():
                if factory == other: continue
                accval += other.owner * other.cyborgs / self.dist(factory, other)
            factory.accessibility = accval

    def dist(self, f1, f2):
        return self.connection[f1.fid][f2.fid]

    def findMeCyborgs(self, target, required):
        sources = []
        for possible_source in self.factory.values():
            ps = possible_source
            if ps.owner != 1:
                continue
            if ps.fid == target.fid:
                continue
            if ps.cyborgs == 0:
                continue
            dist = self.dist(ps, target)
            rate = (required+dist) / ps.cyborgs
            ps.score_as_source = dist * rate
            sources.append(ps)

        sources.sort(key=lambda f:f.score_as_source)
        return sources
    
    def nextSteps(self):
        self.completeUpdate()
        def score(factory):
            return factory.current_value * (factory.production + 0.1) * factory.accessibility

        all_factories = list(self.factory.values())
        for factory in all_factories:
            factory.score = score(factory)

        factories = [ f for f in all_factories if f.score <= 0 and f.production > 0 ]
        if not factories:
            factories = [ f for f in all_factories if f.score <= 0 ]
            if not factories:
                msg = "No idea for a target."
                log(msg)
                return ["WAIT; MSG "+msg]

        factories.sort(key=lambda f:abs(f.score))
        commands = []
        for target in factories:
            log("Chose %s from %s"%(target.fid, ",".join([str(f.fid) for f in factories]), ))
            required_cyborgs = abs(target.current_value) + 1
            cyborg_sources = self.findMeCyborgs(target, required_cyborgs)
            if not cyborg_sources:
                break
            
            source = cyborg_sources[0]
            if (target.owner != 0):
                required_cyborgs += self.dist(source, target) * target.production + 1

            command = "MOVE %d %d %d"%(source.fid, target.fid, required_cyborgs,)
            commands.append(command)
            source.cyborgs = max(source.cyborgs - required_cyborgs, 0)

        if not commands:
            msg = "No cyborgs at hand."
            log(msg)
            return ["WAIT;MSG "+msg]

        return commands
            

    def dumpFactories(self):
        for f in self.factory.values():
            log("F%d: %s %s %s %s"%(f.fid, f.current_value, f.score, f.score_as_source, f.production)) 



def codingame():
    factory_count = int(input())  # the number of factories
    shell = GhostInTheShell(factory_count)

    link_count = int(input())  # the number of links between factories
    for i in range(link_count):
        factory_1, factory_2, distance = [int(j) for j in input().split()]
        shell.connect(factory_1, factory_2, distance)

    # game loop
    while True:
        shell.turn()
        entity_count = int(input())  # the number of entities (e.g. factories and troops)
        for i in range(entity_count):
            entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
            entity_id = int(entity_id)
            arg_1 = int(arg_1)
            arg_2 = int(arg_2)
            arg_3 = int(arg_3)
            arg_4 = int(arg_4)
            arg_5 = int(arg_5)
            update = shell.updateFactory if entity_type == "FACTORY" else shell.updateTroop
            update(entity_id, arg_1, arg_2, arg_3, arg_4, arg_5)


        # Any valid action, such as "WAIT" or "MOVE source destination cyborgs"
        script = ";".join(shell.nextSteps())
        print(script)

        shell.dumpFactories()

if __name__ == "__main__":
    codingame()
