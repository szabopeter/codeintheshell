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
    def testThePlan_singleBigTroopTowardsNeutral(self):
        plan = BombPlan(2)
        uniprod = 0
        my_factory = Factory(0, US, 0, uniprod)
        ef1 = Factory(1, THEM, 0, uniprod)
        ef2 = Factory(2, THEM, 0, uniprod)
        plan.registerSource(ef1, my_factory, 1, 99)
        plan.registerSource(ef2, my_factory, 1, 99)
        army = Troop(100, THEM, ef1.fid, ef2.fid, 10, 1)
        plan.registerTroop(army.going_to, army.turns_left, army.cyborgs)

        source, target = plan.thePlan(10+2)
        self.assertIsNotNone(source)
        self.assertIsNotNone(target)
        self.assertEqual(source, my_factory)
        self.assertEqual(target, ef2)



if __name__ == '__main__':
    unittest.main()
