#!/usr/bin/python3
import sys
import argparse
import random
from scoring import Scoring
from sessions import get_possible_sessions
from random_search import RandomSearch
from incremental_genetic import IncrementalGenetic
import output
from pubsub import PubSub, MQTTClient

random.seed()

status_frequency = 1000
strategies = {'randomSearch' : RandomSearch, 'incrementalGenetic' : IncrementalGenetic}
strategy_names = sorted(list(strategies.keys()))


def build_parser():
  parser = argparse.ArgumentParser(description='Generate best driver dance card')
  parser.add_argument('--cars', metavar='N', type=int, default=4, help='number of cars (default is 4)')
  parser.add_argument('--sessions', metavar='N', type=int, default=12, help='number of sessions (default is 12)')
  parser.add_argument('--strategy', choices=strategy_names, default='incrementalGenetic', help='strategy to use (default is incrementalGenetic)')

  group = parser.add_argument_group('strategy-specific parameters')
  group.add_argument('--population', metavar='N', type=int, default=10000, help='size of population for genetic strategies (default 10000)')
  group.add_argument('--mutation-rate', metavar='N', type=int, default=100, help='mutation rate, expressed as 1 in N (default 100)')
  group.add_argument('--fittest-selections', metavar='N', type=int, default=5, help='number of individuals to sample for best-of-n fittest selection strategy (default 5)')
  group.add_argument('--weakest-selections', metavar='N', type=int, default=5, help='number of individuals to sample for worst-of-n weakest selection strategy (default 5)')

  group = parser.add_argument_group('output controls')
  group.add_argument('--output-stats', action='store_true', help='outputs ongoing statistics to stderr')
  group.add_argument('--score-details', action='store_true', help='outputs details of score calculation with each dance card')

  mqtt_group = parser.add_argument_group('MQTT settings')
  mqtt_group.add_argument('--mqtt-host', metavar='host[:port]', help='MQTT broker host[:port].  If specified, this will cause the process to connect to the MQTT broker and publish state information')
  mqtt_group.add_argument('--mqtt-topic', metavar='topic', default='dancecard', help='root topic for MQTT, below which nodes will publish state (default "dancecard")')

  command_parsers = {}
  subparsers = parser.add_subparsers(dest='command', help='sub-commands')

  help_parser = subparsers.add_parser('help', help='show help for a strategy or a sub-command')
  help_parser.add_argument('command_name', nargs='?', help='either a sub-command or a strategy name')
  command_parsers['help'] = help_parser

  start_parser = subparsers.add_parser('start', help='start a new distributed calc')
  start_parser.add_argument('-f', '--follow', action='store_true', help='continues to monitor status')
  command_parsers['start'] = start_parser

  status_parser = subparsers.add_parser('status', help='show current status of a distributed calc')
  status_parser.add_argument('-f', '--follow', action='store_true', help='continues to monitor status')
  command_parsers['status'] = status_parser

  worker_parser = subparsers.add_parser('worker', help='run as a worker node')
  command_parsers['worker'] = worker_parser

  return parser, command_parsers


def main():
  parser, command_parsers = build_parser()
  args = parser.parse_args()

  if args.command == 'help':
    help(args, command_parsers)
    exit(0)
  else:
    standalone(args)

def standalone(args):
  num_cars = args.cars
  num_people = num_cars * 2
  num_sessions = args.sessions

  publishers = get_publishers(args)
  publishers.publish_scenario(num_cars, num_people, num_sessions)

  possible_sessions = get_possible_sessions(num_people, num_cars)
  generator = lambda : generate_random_dance(possible_sessions, num_sessions)
  scoring = Scoring(num_cars, num_people, num_sessions)

  strategy = strategies[args.strategy](args, generator, scoring)
  publishers.publish_settings(strategy.get_settings())
  run_strategy(strategy, publishers)

def run_strategy(strategy, publishers, cards_output_file=sys.stdout, stats_output_file=sys.stderr):
  strategy.startup()
  count = 0
  last_output = None
  while True:
    strategy.iterate()
    if strategy.best_candidate != last_output:
      last_output = strategy.best_candidate
      print()
      publishers.publish_best(last_output)
    if count % status_frequency == 0:
      best, mean, std_dev = strategy.get_stats()
      publishers.publish_stats(count, best, mean, std_dev)
    count = count + 1
 
def generate_random_dance(possible_sessions, num_sessions):
  sessions = len(possible_sessions)
  dance = []
  for i in range(num_sessions):
    r = random.randrange(0, sessions)
    dance.append(possible_sessions[r])
  return dance

def get_publishers(args):
  publishers = output.Multipublisher()
  publishers.add(output.FileBestOutputter(sys.stdout))
  if args.score_details:
    publishers.add(output.FileDetailedScoresOutputter(sys.stdout))
  if args.output_stats:
    publishers.add(output.FileStatsOutputter(sys.stderr))
  publishers.add(output.FileScenarioOutputter(sys.stderr))
  publishers.add(output.FileSettingsOutputter(sys.stderr))
  if args.mqtt_host:
    publishers.add(PubSub(MQTTClient(args)))
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