#!/usr/bin/python3

import random
from scoring import Scoring
from sessions import get_possible_sessions
from output import output_dance_stats

# Main params
num_cars = 4
num_people = num_cars * 2
num_sessions = 12

status_frequency = 10000
random.seed()
scoring = Scoring(num_cars, num_people, num_sessions)

def main():
  print("Enumerating sessions")
  possible_sessions = get_possible_sessions(num_people, num_cars)
  random_search(possible_sessions)

def random_search(possible_sessions):
  print("Running random search")
  best_scores = None
  count = 0
  while True:
    count = count + 1
    d = generate_random_dance(possible_sessions)
    scores = scoring.score(d)
    if best_scores is None or scores.score > best_scores.score:
      best_scores = scores
      output_dance_stats(scores, num_cars)
    if count % status_frequency == 0:
      print(count)
      output_dance_stats(best_scores, num_cars)
 
def generate_random_dance(possible_sessions):
  sessions = len(possible_sessions)
  dance = []
  for i in range(num_sessions):
    r = random.randrange(0, sessions)
    dance.append(possible_sessions[r])
  return dance

main()