#!/usr/bin/python3

import random
from scoring import Scoring
from sessions import get_possible_sessions
from random_search import RandomSearch
from incremental_genetic import IncrementalGenetic

# Main params
num_cars = 4
num_people = num_cars * 2
num_sessions = 12

population_size = 10000

random.seed()
scoring = Scoring(num_cars, num_people, num_sessions)

def main():
  print("Enumerating sessions")
  possible_sessions = get_possible_sessions(num_people, num_cars)
  generator = lambda : generate_random_dance(possible_sessions)

  #RandomSearch(generator, scoring).run()
  IncrementalGenetic(population_size, generator, scoring).run()
 
def generate_random_dance(possible_sessions):
  sessions = len(possible_sessions)
  dance = []
  for i in range(num_sessions):
    r = random.randrange(0, sessions)
    dance.append(possible_sessions[r])
  return dance

main()