
import sys
import random
from time import time
from scoring import Scoring
from sessions import get_possible_sessions
from threading import Event, Thread
from strategy import Candidate

status_frequency = 1000
sample_size = 5
publish_throttle = 2    # Seconds

class StrategyDriver(object):
  """Responsible for executing the strategy"""
  def __init__(self, scenario, strategy_factory, publishers, importer, import_frequency):
    self.scenario = scenario
    self.strategy_factory = strategy_factory
    self.publishers = publishers
    self.importer = importer
    self.import_frequency = import_frequency
    self.stop_event = Event()
    self.background_thread = None
  
  def run_strategy(self, background=False):
    scoring = Scoring(self.scenario)
    strategy = self.strategy_factory(self._generate_random_dance, scoring)
    self.publishers.publish_scenario(self.scenario)
    self.publishers.publish_settings(strategy.get_settings())
    self.publishers.publish_stats(0, 0, 0, 0)
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
    count = 0
    self.possible_sessions = get_possible_sessions(self.scenario)
    strategy.startup()
    last_output = None
    next_time = time()
    while True:
      if count % status_frequency == 0 and time() > next_time:
        best, mean, std_dev = strategy.get_stats()
        self.publishers.publish_stats(count, best, mean, std_dev)
        self.publishers.publish_sample(self.scenario.id, strategy.get_sample(sample_size))
        next_time = next_time + publish_throttle
      if self.import_frequency > 0 and count % self.import_frequency == 0:
        import_dance = self.importer.get_import(self.scenario.id)
        if import_dance:
          strategy.import_dance(import_dance)
      strategy.iterate()
      if strategy.best_candidate != last_output:
        last_output = strategy.best_candidate
        print()
        self.publishers.publish_best(last_output)
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
