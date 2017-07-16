
import random
from scoring import Scoring
from sessions import get_possible_sessions
from threading import Event

status_frequency = 1000

class StrategyDriver(object):
  """Responsible for executing the strategy"""
  def __init__(self, scenario, publishers):
    self.scenario = scenario
    self.publishers = publishers
  
  def run_strategy(self, strategy):
    self.publishers.publish_scenario(self.scenario)
    self.possible_sessions = get_possible_sessions(self.scenario)
    self.publishers.publish_settings(strategy.get_settings())
    try:
      self._run_strategy(strategy)
    except KeyboardInterrupt:
      print('Interrupted')

  def _run_strategy(self, strategy, stop_event = None):
    strategy.startup()
    count = 0
    last_output = None
    while True:
      strategy.iterate()
      if strategy.best_candidate != last_output:
        last_output = strategy.best_candidate
        print()
        self.publishers.publish_best(last_output)
      if count % status_frequency == 0:
        best, mean, std_dev = strategy.get_stats()
        self.publishers.publish_stats(count, best, mean, std_dev)
      count = count + 1
      if stop_event and stop_event.is_set():
        break
 
  def generate_random_dance(self):
    num_sessions = self.scenario.num_sessions
    sessions = len(self.possible_sessions)
    dance = []
    for i in range(num_sessions):
      r = random.randrange(0, sessions)
      dance.append(self.possible_sessions[r])
    return dance
