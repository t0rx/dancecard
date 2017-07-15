#!/usr/bin/python3
import argparse
import random
from scoring import Scoring
from sessions import get_possible_sessions
from random_search import RandomSearch
from incremental_genetic import IncrementalGenetic

random.seed()

def build_parser():
  parser = argparse.ArgumentParser(description='Generate best driver dance card')
  parser.add_argument('--cars', metavar='N', type=int, default=4, help='number of cars (default is 4)')
  parser.add_argument('--sessions', metavar='N', type=int, default=12, help='number of sessions (default is 12)')
  #parser.add_argument('--strategy', choices=['randomSearch', 'geneticSampling'], default='geneticSampling', help='Strategy to use (default is geneticSampling)')

  group = parser.add_argument_group('strategy-specific parameters')
  group.add_argument('--population', metavar='N', type=int, default=10000, help='size of population for genetic strategies (default 10000)')
  group.add_argument('--mutation-rate', metavar='N', type=int, default=100, help='mutation rate, expressed as 1 in N (default 100)')
  group.add_argument('--fittest-selections', metavar='N', type=int, default=5, help='number of individuals to sample for best-of-n fittest selection strategy (default 5)')
  group.add_argument('--weakest-selections', metavar='N', type=int, default=5, help='number of individuals to sample for worst-of-n weakest selection strategy (default 5)')
  return parser

def main():
  args = build_parser().parse_args()

  num_cars = args.cars
  num_people = num_cars * 2
  num_sessions = args.sessions

  print("Enumerating sessions for %s cars over %s sessions" % (num_cars, num_sessions))
  possible_sessions = get_possible_sessions(num_people, num_cars)
  generator = lambda : generate_random_dance(possible_sessions, num_sessions)
  scoring = Scoring(num_cars, num_people, num_sessions)

  #RandomSearch(args, generator, scoring).run()
  IncrementalGenetic(args, generator, scoring).run()
 
def generate_random_dance(possible_sessions, num_sessions):
  sessions = len(possible_sessions)
  dance = []
  for i in range(num_sessions):
    r = random.randrange(0, sessions)
    dance.append(possible_sessions[r])
  return dance

main()