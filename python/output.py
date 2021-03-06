#!/usr/bin/python3

# Utility functions for outputting stuff
import sys
from sessions import Scenario

class Publisher(object):
  def publish_scenario(self, scenario):
    pass

  def publish_stats(self, count, best, mean, std_dev):
    pass

  def publish_best(self, best):
    pass

  def publish_sample(self, scenario_id, sample):
    pass

  def publish_settings(self, settings):
    pass


class FileBestOutputter(Publisher):
  def __init__(self, file):
    self.file = file

  def publish_best(self, best):
    print(best.scores.total_score, file=self.file)
    print(format_dance(best.dance), file=self.file)
    self.file.flush()


class FileDetailedScoresOutputter(Publisher):
  def __init__(self, file):
    self.file = file

  def publish_best(self, best):
    scores = best.scores
    print("Car distance scores:", sum(scores.car_distances), scores.car_distances, file=self.file)
    print("People scores:", sum(scores.people_distances), scores.people_distances, file=self.file)
    print("Car distribution scores:", sum(scores.car_balances), scores.car_balances, file=self.file)
    print(format_people_car_matrix(scores.people_car_matrix), file=self.file)
    self.file.flush()


class FileStatsOutputter(Publisher):
  def __init__(self, file):
    self.file = file

  def publish_stats(self, count, best, mean, std_dev):
    print(count, best, mean, std_dev, file=self.file)
    self.file.flush()


class FileSettingsOutputter(Publisher):
  def __init__(self, file):
    self.file = file

  def publish_settings(self, settings):
    print('Strategy settings: %s' % str(settings), file=self.file)
    self.file.flush()


class FileScenarioOutputter(Publisher):
  def __init__(self, file):
    self.file = file

  def publish_scenario(self, scenario):
    print("Scenario: %s, cars: %d, people: %d, sessions: %d" % (scenario.id, scenario.num_cars, scenario.num_people, scenario.num_sessions), file=self.file)
    self.file.flush()


class Multipublisher(Publisher):
  def __init__(self):
    self.sub_publishers = []

  def add(self, publisher):
    self.sub_publishers.append(publisher)

  def publish_scenario(self, scenario):
    for p in self.sub_publishers:
      p.publish_scenario(scenario)

  def publish_stats(self, count, best, mean, std_dev):
    for p in self.sub_publishers:
      p.publish_stats(count, best, mean, std_dev)

  def publish_best(self, best):
    for p in self.sub_publishers:
      p.publish_best(best)

  def publish_sample(self, scenario_id, sample):
    for p in self.sub_publishers:
      p.publish_sample(scenario_id, sample)

  def publish_settings(self, settings):
    for p in self.sub_publishers:
      p.publish_settings(settings)


def format_people_car_matrix(m):
  return '\n'.join([' '.join([str(x) for x in car]) for car in m])

def format_dance(dance):
  num_cars = len(dance[0])
  result = ''
  for i in range(num_cars):
    result = result + ' '.join([format_pair(session[i]) for session in dance]) + '\n'
  return result.strip()

def format_session(session):
  return ' '.join([format_pair(pair) for pair in session])

def format_pair(pair):
  a, b = pair
  return chr(a + ord('A')) + chr(b + ord('A'))

def decode_pair(s):
  return [ord(s[0]) - ord('A'), ord(s[1]) - ord('A')]

def decode_dance(s):
  rows = s.split('\n')
  data = [row.split(' ') for row in rows]
  num_sessions = len(data[0])
  # The format is oriented the other way around
  dance = [[decode_pair(data[r][c]) for r in range(len(data))] for c in range(num_sessions)]
  return dance
