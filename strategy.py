import sys
from scoring import Scoring
from output import output_dance_stats

status_frequency = 1000

class Candidate(object):
  def __init__(self, dance, scores):
    self.dance = dance
    self.scores = scores

class Strategy(object):
  def __init__(self, name, random_dance_generator, scoring):
    self.name = name
    self._random_dance_generator = random_dance_generator
    self._scoring = scoring
    self._best_candidate = None

  def iterate(self):
    """Override this to do work"""
    pass

  def run(self, cards_output_file=sys.stdout, stats_output_file=sys.stderr):
    self.print_settings(file=stats_output_file)
    count = 0
    last_output = None
    while True:
      self.iterate()
      if count % status_frequency == 0:
        self.output_stats(count, file=stats_output_file)
        stats_output_file.flush()
        if self._best_candidate != last_output:
          last_output = self._best_candidate
          output_dance_stats(last_output, cards_output_file)
          cards_output_file.flush()
      count = count + 1

  def print_settings(self, file):
    print("Algorithm=%s" % self.name, file=file)

  def output_stats(self, count, file):
    print(count, self._best_candidate.scores.total_score, file=file)

  def generate_dance(self):
    return self._random_dance_generator()

  def create_candidate(self, dance):
    scores = self.score(dance)
    return Candidate(dance, scores)

  def create_and_track_candidate(self, dance):
    """Creates a new Candidate for the dance, updating best known scores"""
    candidate = self.create_candidate(dance)
    self.track_best(candidate)
    return candidate

  def score(self, dance):
    return self._scoring.score(dance)

  def track_best(self, candidate):
    if self._best_candidate is None or candidate.scores.total_score > self._best_candidate.scores.total_score:
      self._best_candidate = candidate
