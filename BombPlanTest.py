import unittest

from ghostInTheCell import *


def id_generator():
    nextid = 1
    while True:
        yield nextid
        nextid += 1


idgenerator = id_generator()


def next_id():
    return idgenerator.__next__()


class BombPlanTestCase(unittest.TestCase):
    def calcBigArmyLimit(self, *args):
        total_troop_size = sum(args)
        return int(total_troop_size / (1 / BIGTROOP - 1))

    def testThePlan_bombSingleBigTroopTowardsNeutral(self):
        plan = BombPlan(2)
        uniprod = 0
        ef1_garrison, ef2_garrison, = 0, 0
        marching = self.calcBigArmyLimit(ef1_garrison, ef2_garrison) + 1
        my_factory = Factory(0, US, 0, uniprod)
        ef1 = Factory(1, THEM, ef1_garrison, uniprod)
        ef2 = Factory(2, THEM, ef2_garrison, uniprod)
        plan.registerSource(ef1, my_factory, 1, 99)
        plan.registerSource(ef2, my_factory, 1, 99)
        army_to, army_turns, army_size = ef2.fid, 1, marching
        plan.registerTroop(army_to, army_turns, army_size)
        source, target = plan.thePlan(ef1_garrison + ef2_garrison + marching)
        self.assertIsNotNone(source)
        self.assertIsNotNone(target)
        self.assertEqual(source, my_factory)
        self.assertEqual(target, ef2)

    def testThePlan_ignoreSingleSmallTroop(self):
        plan = BombPlan(2)
        uniprod = 0
        ef1_garrison, ef2_garrison, = 0, 0
        marching = self.calcBigArmyLimit(ef1_garrison, ef2_garrison) - 1
        my_factory = Factory(0, US, 0, uniprod)
        ef1 = Factory(1, THEM, ef1_garrison, uniprod)
        ef2 = Factory(2, THEM, ef2_garrison, uniprod)
        plan.registerSource(ef1, my_factory, 1, 99)
        plan.registerSource(ef2, my_factory, 1, 99)
        army_to, army_turns, army_size = ef2.fid, 1, marching
        plan.registerTroop(army_to, army_turns, army_size)
        source, target = plan.thePlan(ef1_garrison + ef2_garrison + marching)
        self.assertIsNone(source)
        self.assertIsNone(target)

    def testThePlan_bombTwoSmallTroopsTowardsNeutral(self):
        plan = BombPlan(2)
        uniprod = 0
        ef1_garrison, ef2_garrison, = 0, 0
        marching = self.calcBigArmyLimit(ef1_garrison, ef2_garrison) + 1
        army1_size = marching // 2 - marching%2
        army2_size = marching // 2 + marching%2
        my_factory = Factory(0, US, 0, uniprod)
        ef1 = Factory(1, THEM, ef1_garrison, uniprod)
        ef2 = Factory(2, THEM, ef2_garrison, uniprod)
        plan.registerSource(ef1, my_factory, 1, 99)
        plan.registerSource(ef2, my_factory, 1, 99)
        army1_to, army1_turns, army1_size = ef2.fid, 1, army1_size
        army2_to, army2_turns, army2_size = ef2.fid, 1, army2_size
        plan.registerTroop(army1_to, army1_turns, army1_size)
        plan.registerTroop(army2_to, army2_turns, army2_size)
        source, target = plan.thePlan(ef1_garrison + ef2_garrison + army1_size + army2_size)
        self.assertIsNotNone(source)
        self.assertIsNotNone(target)
        self.assertEqual(source, my_factory)
        self.assertEqual(target, ef2)

if __name__ == '__main__':
    unittest.main()
