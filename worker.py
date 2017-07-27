#!/usr/bin/python3
import sys
import threading
import yaml
from sessions import Scenario
from driver import StrategyDriver

class Worker(object):
  def __init__(self, mqtt_client, strategy_factory, publishers, importer, import_frequency, worker_name):
    self.mqtt_client = mqtt_client
    self.strategy_factory = strategy_factory
    self.publishers = publishers
    self.importer = importer
    self.import_frequency = import_frequency
    self.name = worker_name
    self.running_driver = None
    self.running_scenario = None
    self.lock = threading.RLock()

  def listen(self):
    self.mqtt_client.publish_status('idle')
    if self.name:
      self.mqtt_client.publish('name', self.name, retain=True)
    self.mqtt_client.subscribe('control/active_scenario', self._received_scenario_message)
    print('Listening for new scenarios', file=sys.stderr)

  def stop(self):
    self._stop_running_scenario()

  def _received_scenario_message(self, message):
    try:
      obj = yaml.safe_load(message.payload)
      if obj is None:
        print("Couldn't decode message so ignoring: %s" % message.payload, file=sys.stderr)
        return
      
      if obj == {}:
        print("Received no active scenario", file=sys.stderr)
        self._stop_running_scenario()
        self.mqtt_client.publish_status('idle')
        print("Waiting for new scenario", file=sys.stderr)
      else:
        scenario = Scenario.from_dict(obj)
        self.mqtt_client.publish_status('active')
        self._run_new_scenario(scenario)
    except Exception as e:
      print("Exception processing message - ignoring: %s" % str(e), file=sys.stderr)

  def _run_new_scenario(self, scenario):
    with self.lock:
      self._stop_running_scenario()
      print('Starting new scenario %s' % scenario.id, file=sys.stderr)
      self.running_scenario = scenario      
      self.running_driver = StrategyDriver(scenario, self.strategy_factory, self.publishers, self.importer, self.import_frequency)
      self.running_driver.run_strategy(True)

  def _stop_running_scenario(self):
    with self.lock:
      if self.running_driver:
        print('Stopping scenario %s' % self.running_scenario.id, file=sys.stderr)
        self.running_driver.stop()
        self.running_driver = None
        self.running_scenario = None
