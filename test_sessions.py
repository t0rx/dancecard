#!/usr/bin/python3

import sys
import unittest
from sessions import *

class TestSessions(unittest.TestCase):
  def test_scenario_hash(self):
    scenario1 = Scenario("id1", 3, 4, 5)
    scenario2 = Scenario("id2", 4, 5, 6)
    self.assertNotEqual(scenario1.hash_str(), scenario2.hash_str())

  def test_scenario_id_not_in_hash(self):
    scenario1 = Scenario("id1", 3, 4, 5)
    scenario2 = Scenario("id2", 3, 4, 5)
    self.assertEqual(scenario1.hash_str(), scenario2.hash_str())


if __name__ == '__main__':
  unittest.main()
