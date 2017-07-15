# Utility functions for outputting stuff
import sys

class Publisher(object):
  def publish_scenario(self, cars, people, sessions):
    pass

  def publish_stats(self, count, best, mean, std_dev):
    pass

  def publish_best(self, best):
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
    print(settings, file=self.file)
    self.file.flush()


class FileScenarioOutputter(Publisher):
  def __init__(self, file):
    self.file = file

  def publish_scenario(self, cars, people, sessions):
    print("Cars: %d, people: %d, sessions: %d" % (cars, people, sessions), file=self.file)
    self.file.flush()


class Multipublisher(Publisher):
  def __init__(self):
    self.sub_publishers = []

  def add(self, publisher):
    self.sub_publishers.append(publisher)

  def publish_scenario(self, cars, people, sessions):
    for p in self.sub_publishers:
      p.publish_scenario(cars, people, sessions)

  def publish_stats(self, count, best, mean, std_dev):
    for p in self.sub_publishers:
      p.publish_stats(count, best, mean, std_dev)

  def publish_best(self, best):
    for p in self.sub_publishers:
      p.publish_best(best)

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
  return chr(a + 65) + chr(b + 65)
