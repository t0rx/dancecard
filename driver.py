
import sys
import random
from scoring import Scoring
from sessions import get_possible_sessions
from threading import Event, Thread

status_frequency = 1000

class StrategyDriver(object):
  """Responsible for executing the strategy"""
  def __init__(self, scenario, strategy_factory, publishers):
    self.scenario = scenario
    self.strategy_factory = strategy_factory
    self.publishers = publishers
    self.stop_event = Event()
    self.background_thread = None
  
  def run_strategy(self, background=False):
    scoring = Scoring(self.scenario)
    strategy = self.strategy_factory(self._generate_random_dance, scoring)
    self.publishers.publish_scenario(self.scenario)
    self.publishers.publish_settings(strategy.get_settings())
    if background:
      self.background_thread = Thread(target=self._run_strategy, args=(strategy,))
      self.background_thread.daemon = True
      self.background_thread.start()
    else:
      self._run_strategy(strategy)

  def stop(self):
    self.stop_event.set()
    if self.background_thread:
      self.background_thread.join()

  def _run_strategy(self, strategy):
    self.possible_sessions = get_possible_sessions(self.scenario)
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
      if self.stop_event.is_set():
        break
 
  def _generate_random_dance(self):
    num_sessions = self.scenario.num_sessions
    sessions = len(self.possible_sessions)
    dance = []
    for i in range(num_sessions):
      r = random.randrange(0, sessions)
      dance.append(self.possible_sessions[r])
    return dance
