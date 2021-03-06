# Session generator
import os
import pickle
import sys
from util import hash_str

class Scenario(object):
  def __init__(self, scenario_id, num_cars, num_people, num_sessions):
    self.id = scenario_id
    self.num_cars = num_cars
    self.num_people = num_people
    self.num_sessions = num_sessions

  def to_dict(self):
    return {'scenario': self.id, 'cars': self.num_cars, 'people': self.num_people, 'sessions': self.num_sessions}

  @staticmethod
  def from_dict(d):
    return Scenario(d['scenario'], int(d['cars']), int(d['people']), int(d['sessions']))

  def hash_str(self):
    d = self.to_dict()
    d.pop('scenario')
    return hash_str(d)

def get_possible_sessions(scenario):
  print("Generating possible sessions... ", end="")
  sys.stdout.flush()
  pairs = get_pairs(scenario.num_people)
  num_pairs = len(pairs)
  num_cars = scenario.num_cars
  indices = [0 for i in range(num_cars)]
  sessions = []
  while True:
    i = 0
    while i < num_cars:
      indices[i] = (indices[i] + 1) % num_pairs
      if indices[i] != 0:
        break
      i = i + 1
    if i == num_cars:
      break
    session = [pairs[i] for i in indices]
    if is_valid_session(session, scenario.num_people):
      sessions.append(session)
  print("done.")
  return sessions

class SessionCache(object):
  def __init__(self, cache_dir):
    self.cache_dir = cache_dir

  def load_or_generate(self, scenario):
    sessions = self._load_from_cache(scenario)
    if not sessions:
      sessions = get_possible_sessions(scenario)
      self._save_to_cache(scenario, sessions)
    return sessions

  def _load_from_cache(self, scenario):
    filename = self.cache_dir + '/' + scenario.hash_str()
    if os.path.exists(filename):
      with open(filename, 'rb') as file:
        return pickle.load(file)
    return None

  def _save_to_cache(self, scenario, sessions):
    if os.path.isdir(self.cache_dir):
      filename = self.cache_dir + '/' + scenario.hash_str()
      with open(filename, 'wb') as file:
        pickle.dump(sessions, file)
    pass

def is_valid_session(session, num_people):
  people = [False] * num_people
  for a, b in session:
    if people[a] or people[b]:
      return False
    people[a] = True
    people[b] = True
  return True

def get_pairs(n):
  all_combs = [[i, j] for i in range(n) for j in range(n) if i != j]
  pairs = []
  for i in all_combs:
    p = sorted(i)
    if p not in pairs:
      pairs.append(p)
  return pairs
