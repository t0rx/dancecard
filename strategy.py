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

  def run(self):
    print("Running %s" % self.name)
    count = 0
    while True:
      count = count + 1
      self.iterate()
      if count % status_frequency == 0:
        print()
        print(count)
        self.output()

  def output(self):
    output_dance_stats(self.best_scores)

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