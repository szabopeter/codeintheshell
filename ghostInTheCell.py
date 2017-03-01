import sys
import math

def log(msg):
    # Write an action using print
    print(msg, file=sys.stderr)


class Factory(object):
    def __init__(self, fid, owner, cyborgs, production):
        self.fid = fid
        self.owner, self.cyborgs, self.production = owner, cyborgs, production
        self.current_value = cyborgs if owner == 1 else -cyborgs
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


class Bomb(object):
    def __init__(self, bid, owner, coming_from, going_to, turns_left):
        self.bid = bid
        self.owner = owner
        self.coming_from, self.going_to = coming_from, going_to
        self.turns_left = turns_left


class GhostInTheShell(object):
    def __init__(self, factory_count):
        self.factory_count = factory_count
        self.connection = {}
        self.bombwatch = []
        self.evacuation_plan = {}
        self.turn = 0

    def connect(self, factid1, factid2, distance):
        log("Connecting %d-%d"%(factid1, factid2,))
        if factid1 not in self.connection:
            self.connection[factid1] = {}
        if factid2 not in self.connection:
            self.connection[factid2] = {}
        self.connection[factid1][factid2] = distance
        self.connection[factid2][factid1] = distance

    def new_turn(self):
        self.factory = {}
        self.troop = {}
        self.bomb = {}
        self.turn += 1
        log("Starting turn %d"%(self.turn,))

    def updateFactory(self, factory_id, owner, cyborgs, production, _unused1, _unused2):
        self.factory[factory_id] = Factory(factory_id, owner, cyborgs, production)

    def updateTroop(self, troop_id, owner, coming_from, going_to, cyborgs, turns_left):
        self.troop[troop_id] = Troop(troop_id, owner, coming_from, going_to, cyborgs, turns_left)

    def updateBomb(self, bomb_id, owner, coming_from, going_to, turns_left, _unused):
        self.bomb[bomb_id] = Bomb(bomb_id, owner, coming_from, going_to, turns_left)
        if owner == -1 and bomb_id not in self.bombwatch:
            #self.bombwatch.append(bomb_id)
            log("They launched a bomb from %d in turn %d"%(coming_from, self.turn,))
            log("Here is the evacuation plan:")
            self.makeEvacuationPlan(coming_from)        

    def makeEvacuationPlan(self, origin):
        for possible_target in self.factory.values():
            impact_turn = self.turn + self.dist(origin, possible_target) - 2
            if impact_turn not in self.evacuation_plan:
                self.evacuation_plan[impact_turn] = []
            self.evacuation_plan[impact_turn].append(possible_target.fid)
            log("Evacuate %d in turn #%d"%(possible_target.fid, impact_turn,))

    def completeUpdate(self):
        for troop in self.troop.values():
            factory = self.factory[troop.going_to]
            factory.markTarget(troop)
        for factory in self.factory.values():
            accval = 0
            for other in self.factory.values():
                if factory == other: continue
                accval += other.owner * other.cyborgs / self.dist(factory, other)
            factory.accessibility = 4/accval if accval != 0 else 99
        self.bombwatch = self.bomb.keys()

    def dist(self, f1, f2):
        fid1 = f1 if type(f1)==type(1) else f1.fid
        fid2 = f2 if type(f2)==type(1) else f2.fid
        if fid1 in self.connection:
            if fid2 in self.connection[fid1]:
                return self.connection[fid1][fid2]
        log("Dist=99 because %d and %d are not connected"%(fid1, fid2,))
        return 99

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
            rate = (required+dist*target.production*(-target.owner)) / ps.cyborgs
            ps.score_as_source = dist * rate
            sources.append(ps)

        sources.sort(key=lambda f:f.score_as_source)
        return sources
    
    def nextSteps(self):
        self.completeUpdate()
        def score(factory):
            return factory.current_value * (factory.production + 0.1) * 100*factory.accessibility

        all_factories = list(self.factory.values())
        for factory in all_factories:
            factory.score = score(factory)

        factories = [ f for f in all_factories if f.score <= 0 and f.production > 0 ]
        commands = []
        if not factories:
            factories = [ f for f in all_factories if f.score <= 0 ]
            if not factories:
                msg = "No idea for a target."
                log(msg)
                commands.extend(["WAIT; MSG "+msg])

        factories.sort(key=lambda f:abs(f.score))
        for target in factories:
            log("Chose %s from %s"%(target.fid, ",".join([str(f.fid) for f in factories]), ))
            required_cyborgs = abs(target.current_value)
            cyborg_sources = self.findMeCyborgs(target, required_cyborgs)
            if not cyborg_sources:
                log("Can't mobilize any cyborgs for %d"%(target.fid,))
                continue
            
            source = cyborg_sources[0]
            if (target.owner != 0):
                extra_cyborgs = (self.dist(source, target)+1) * target.production + 1
                log("Dispatching %d+%d cyborgs from %s (has %d) to %d"%(required_cyborgs, extra_cyborgs, source.fid, source.cyborgs, target.fid,))
                required_cyborgs += extra_cyborgs
            else:
                required_cyborgs += 1
                log("Dispatching %d cyborgs from %s (has %d) to neutral %d"%(required_cyborgs, source.fid, source.cyborgs, target.fid,))

            command = "MOVE %d %d %d"%(source.fid, target.fid, required_cyborgs,)
            commands.append(command)
            source.cyborgs = max(source.cyborgs - required_cyborgs, 0)

        if self.turn in self.evacuation_plan:
            for panicking_fid in self.evacuation_plan[self.turn]:
                panicking = self.factory[panicking_fid]
                if panicking.owner != 1: continue
                msg = "MSG RUN, YOU FOOLS! All %d of you at %d!"%(panicking.cyborgs, panicking.fid,)
                commands.append(msg)
                log(msg)
                fact = self.factory[panicking.fid]
                log("WTF: %d =?= %d"%(fact.cyborgs, panicking.cyborgs,))
                while panicking.cyborgs > 0:
                    for anywhere in self.factory.values():
                        if anywhere.fid == panicking.fid: continue
                        commands.append("MOVE %d %d 1"%(panicking.fid, anywhere.fid,))
                        panicking.cyborgs -= 1
                        if panicking.cyborgs == 0:
                            break
            del self.evacuation_plan[self.turn]
                    
        if not commands:
            msg = "No cyborgs at hand."
            log(msg)
            return ["WAIT;MSG "+msg]

        return commands
            
    def readyToStrike(self, fid, turns_left):
        target = self.factory[fid]
        for factory in self.factory.values():
            if factory.owner != 1: continue
            dist = self.dist(factory, target)
            if dist == turns_left:
                return factory
        return None

    def bombMaybe(self):
        hostiles = [ troop for troop in self.troop.values() if troop.owner == -1 ]
        hostile_garrisons = sum([ factory.cyborgs for factory in self.factory.values() if factory.owner == -1])
        army_size = sum([troop.cyborgs for troop in hostiles]) + hostile_garrisons
        hostiles.sort(key = lambda t:-t.cyborgs -5*self.factory[t.going_to].production)
        for hostile in hostiles:
            if hostile.cyborgs < army_size * 0.15:
                continue
            target = self.factory[hostile.going_to]
            if target.current_value >= 0:
                continue
            source = self.readyToStrike(target.fid, hostile.turns_left)
            if not source:
                continue
            log("Dropping a bomb, because %d approaching hostiles (%d total) and current value of %s."\
                %(hostile.cyborgs, army_size, target.current_value,))
            return ["BOMB %d %d"%(source.fid, target.fid,)]
        return []


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
        shell.new_turn()
        entity_count = int(input())  # the number of entities (e.g. factories and troops)
        for i in range(entity_count):
            entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
            entity_id = int(entity_id)
            arg_1 = int(arg_1)
            arg_2 = int(arg_2)
            arg_3 = int(arg_3)
            arg_4 = int(arg_4)
            arg_5 = int(arg_5)
            update_methods = \
                {
                "FACTORY" : shell.updateFactory,
                "TROOP" : shell.updateTroop,
                "BOMB" : shell.updateBomb,
                }
            update = update_methods[entity_type]
            update(entity_id, arg_1, arg_2, arg_3, arg_4, arg_5)


        # Any valid action, such as "WAIT" or "MOVE source destination cyborgs"
        commands = shell.nextSteps()
        commands.extend(shell.bombMaybe())
        script = ";".join(commands)
        print(script)

        shell.dumpFactories()

if __name__ == "__main__":
    codingame()
