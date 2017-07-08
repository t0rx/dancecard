import sys
from scoring import Scoring
from output import output_dance_stats

status_frequency = 1000

class Strategy(object):
  def __init__(self, name, random_dance_generator, scoring):
    self.name = name
    self.random_dance_generator = random_dance_generator
    self.scoring = scoring
    self.best_scores = None

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
        if self.best_scores != last_output:
          last_output = self.best_scores
          output_dance_stats(last_output, cards_output_file)
      count = count + 1

  def print_settings(self, file):
    print("Algorithm=%s" % self.name, file=file)

  def output_stats(self, count, file):
    print(count, self.best_scores.total_score, file=file)

  def score_and_track(self, dance):
    """Scores a new dance and tracks best known for outputting"""
    scores = self.scoring.score(dance)
    if self.best_scores is None or scores.total_score > self.best_scores.total_score:
      self.best_scores = scores
    return scores

  def generate_and_score(self):
    """Generates a new random dance and scores it, updating best known scores"""
    d = self.random_dance_generator()
    return self.score_and_track(d)