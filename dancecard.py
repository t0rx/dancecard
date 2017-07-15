#!/usr/bin/python3
import argparse
import random
from scoring import Scoring
from sessions import get_possible_sessions
from random_search import RandomSearch
from incremental_genetic import IncrementalGenetic

random.seed()

strategies = {'randomSearch' : RandomSearch, 'incrementalGenetic' : IncrementalGenetic}
strategy_names = sorted(list(strategies.keys()))

def build_parser():
  parser = argparse.ArgumentParser(description='Generate best driver dance card')
  parser.add_argument('--cars', metavar='N', type=int, default=4, help='number of cars (default is 4)')
  parser.add_argument('--sessions', metavar='N', type=int, default=12, help='number of sessions (default is 12)')
  parser.add_argument('--strategy', choices=strategy_names, default='incrementalGenetic', help='Strategy to use (default is incrementalGenetic)')

  group = parser.add_argument_group('strategy-specific parameters')
  group.add_argument('--population', metavar='N', type=int, default=10000, help='size of population for genetic strategies (default 10000)')
  group.add_argument('--mutation-rate', metavar='N', type=int, default=100, help='mutation rate, expressed as 1 in N (default 100)')
  group.add_argument('--fittest-selections', metavar='N', type=int, default=5, help='number of individuals to sample for best-of-n fittest selection strategy (default 5)')
  group.add_argument('--weakest-selections', metavar='N', type=int, default=5, help='number of individuals to sample for worst-of-n weakest selection strategy (default 5)')

  subparsers = parser.add_subparsers(help='show help for a specific strategy')
  help_parser = subparsers.add_parser('help')
  help_parser.add_argument('help_strategy', choices=strategy_names, nargs='?')

  return parser

def main():
  parser = build_parser()
  args = parser.parse_args()

  if 'help_strategy' in args:
    help(args)
    exit(0)

  num_cars = args.cars
  num_people = num_cars * 2
  num_sessions = args.sessions

  print("Enumerating sessions for %s cars over %s sessions" % (num_cars, num_sessions))
  possible_sessions = get_possible_sessions(num_people, num_cars)
  generator = lambda : generate_random_dance(possible_sessions, num_sessions)
  scoring = Scoring(num_cars, num_people, num_sessions)

  strategy = strategies[args.strategy]
  strategy(args, generator, scoring).run()
 
def generate_random_dance(possible_sessions, num_sessions):
  sessions = len(possible_sessions)
  dance = []
  for i in range(num_sessions):
    r = random.randrange(0, sessions)
    dance.append(possible_sessions[r])
  return dance

def help(args):
  name = args.help_strategy
  if name:
    s = [name]
  else:
    s = strategy_names

  for name in s:
    print('Help for %s:' % name)
    print(strategies[name].__doc__)

main()