#!/usr/bin/python3
import argparse
import os
import random
import sys
import yaml
from time import sleep
from scoring import Scoring
from random_search import RandomSearch
from incremental_genetic import IncrementalGenetic
import output
from mqtt import MQTTPublisher, MQTTClient, MQTTConfig
from util import new_scenario_id, extant_file, MapNamespace, hyphen_to_underscore
from sessions import Scenario
from driver import StrategyDriver
from worker import Worker
from tracker import Tracker
from importer import ImportSource, MQTTImporter

random.seed()

default_args = {'cars': 4,
                'sessions': 12,
                'strategy': 'incrementalGenetic',
                'population': 10000,
                'mutation_rate': 100,
                'fittest_selections': 5,
                'weakest_selections': 5,
                'import_frequency': 0,
                'initial_pause': 1,
                'delay': 5}

status_frequency = 1000
strategies = {'randomSearch' : RandomSearch, 'incrementalGenetic' : IncrementalGenetic}
strategy_names = sorted(list(strategies.keys()))


def build_parser():
  parser = argparse.ArgumentParser(description='Generate best driver dance card')
  parser.add_argument('--config', type=extant_file, help='YAML file containing configuration.  Other command-line args will override setting from this file.')
  parser.add_argument('--cars', metavar='N', type=int, help='number of cars (default is 4)')
  parser.add_argument('--sessions', metavar='N', type=int, help='number of sessions (default is 12)')
  parser.add_argument('--strategy', choices=strategy_names, help='strategy to use (default is incrementalGenetic)')

  group = parser.add_argument_group('strategy-specific parameters')
  group.add_argument('--population', metavar='N', type=int, help='size of population for genetic strategies (default 10000)')
  group.add_argument('--mutation-rate', metavar='N', type=int, help='mutation rate, expressed as 1 in N (default 100)')
  group.add_argument('--fittest-selections', metavar='N', type=int, help='number of individuals to sample for best-of-n fittest selection strategy (default 5)')
  group.add_argument('--weakest-selections', metavar='N', type=int, help='number of individuals to sample for worst-of-n weakest selection strategy (default 5)')
  group.add_argument('--import-frequency', metavar='N', type=int, help='if specified, will import a candidate from a remote worker every N iterations.')

  group = parser.add_argument_group('output controls')
  group.add_argument('--output-stats', action='store_true', help='outputs ongoing statistics to stderr')
  group.add_argument('--score-details', action='store_true', help='outputs details of score calculation with each dance card')

  MQTTConfig.add_argument_group(parser)

  command_parsers = {}
  subparsers = parser.add_subparsers(dest='command', help='sub-commands')

  help_parser = subparsers.add_parser('help', help='show help for a strategy or a sub-command')
  help_parser.add_argument('command_name', nargs='?', help='either a sub-command or a strategy name')
  command_parsers['help'] = help_parser

  start_parser = subparsers.add_parser('start', help='start a new distributed calc')
  start_parser.add_argument('-f', '--follow', action='store_true', help='continues to monitor status')
  command_parsers['start'] = start_parser

  stop_parser = subparsers.add_parser('stop', help='stop the current distributed calc')
  command_parsers['stop'] = stop_parser

  status_parser = subparsers.add_parser('status', help='show current status of a distributed calc')
  status_parser.add_argument('-f', '--follow', action='store_true', help='continues to monitor status')
  status_parser.add_argument('--initial-pause', metavar='N', type=int, help='number of seconds to wait for data when not following')
  status_parser.add_argument('--delay', metavar='N', type=int, help='number of seconds to wait between status output')
  command_parsers['status'] = status_parser

  worker_parser = subparsers.add_parser('worker', help='run as a worker node')
  command_parsers['worker'] = worker_parser

  return parser, command_parsers


def main():
  parser, command_parsers = build_parser()
  args = parser.parse_args()
  config = load_config(args)

  if config.command == 'help':
    help(config, command_parsers)
  elif config.command == 'start':
    start(config)
  elif config.command == 'stop':
    stop(config)
  elif config.command == 'status':
    status(config)
  elif config.command == 'worker':
    worker(config)
  else:
    standalone(config)

def start(args):
  mqtt_client = get_mqtt(args, force=True)
  scenario = get_scenario(args)
  mqtt_client.publish_yaml('control/active_scenario', scenario.to_dict(), retain=True)
  mqtt_client.stop_loop()
  print('Published scenario %s' + scenario.id)

def stop(args):
  mqtt_client = get_mqtt(args, force=True)
  mqtt_client.publish_yaml('control/active_scenario', {}, retain=True)
  mqtt_client.stop_loop()
  print('Published stop command.')

def status(args):
  mqtt_client = get_mqtt(args, force=True)
  tracker = Tracker(mqtt_client, args.initial_pause)
  tracker.listen()
  tracker.print()
  if args.follow:
    try:
      # Just loop until we get killed
      while True:
        sleep(args.delay)
        print()
        tracker.print()
    except KeyboardInterrupt:
      print('Keyboard interrupt.  Stopping.')

def standalone(args):
  mqtt_client = get_mqtt(args)
  publishers = get_publishers(args, mqtt_client)
  strategy_factory = lambda generator, scoring: strategies[args.strategy](args, generator, scoring)
  scenario = get_scenario(args)
  driver = StrategyDriver(scenario, strategy_factory, publishers, ImportSource(), args.import_frequency)
  try:
    driver.run_strategy()
  except KeyboardInterrupt:
    print('Interrupted', file=sys.stderr)

def worker(args):
  mqtt_client = get_mqtt(args, force=True, advertise_node=True)
  publishers = get_publishers(args, mqtt_client)
  importer = MQTTImporter(mqtt_client)
  strategy_factory = lambda generator, scoring: strategies[args.strategy](args, generator, scoring)
  worker = Worker(mqtt_client, strategy_factory, publishers, importer, args.import_frequency)
  worker.listen()
  wait_for_interrupt()
  worker.stop()

def load_config(args):
  config = MapNamespace(default_args)
  merge_config_from_first_file(config, [args.config, './dancecard-config.yaml', '/etc/dancecard/dancecard-config.yaml'])
  config.merge(vars(args))
  return config

def merge_config_from_first_file(config, filenames):
  for filename in filenames:
    if filename and os.path.exists(filename):
      with open(filename) as stream:
        config.merge(hyphen_to_underscore(yaml.load(stream)))
      break

def wait_for_interrupt():
  try:
    # Just loop until we get killed
    while True:
      sleep(100)
  except KeyboardInterrupt:
    print('Keyboard interrupt.  Stopping.')

def get_scenario(args, scenario_id=None):
  if not scenario_id:
    scenario_id = new_scenario_id()
  return Scenario(scenario_id, args.cars, args.cars * 2, args.sessions)

def get_mqtt(args, force=False, advertise_node=False):
  config = MQTTConfig.from_args(args)
  if force and not config:
    print("Must specify MQTT settings for %s command." % args.command, file=sys.stderr)
    exit(1)
  return MQTTClient(config, advertise_node) if config else None

def get_publishers(args, mqtt_client=None):
  publishers = output.Multipublisher()
  publishers.add(output.FileBestOutputter(sys.stdout))
  if args.score_details:
    publishers.add(output.FileDetailedScoresOutputter(sys.stdout))
  if args.output_stats:
    publishers.add(output.FileStatsOutputter(sys.stderr))
  publishers.add(output.FileScenarioOutputter(sys.stderr))
  publishers.add(output.FileSettingsOutputter(sys.stderr))
  if mqtt_client:
    publishers.add(MQTTPublisher(mqtt_client))
  return publishers

def help(args, command_parsers):
  name = args.command_name

  if name in command_parsers:
    command_parsers[name].print_help()
  else:
    if name:
      s = [name]
    else:
      s = strategy_names

    for name in s:
      print('Help for %s:' % name)
      print(strategies[name].__doc__)

main()