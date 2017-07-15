from scoring import Scoring

class Candidate(object):
  def __init__(self, dance, scores):
    self.dance = dance
    self.scores = scores

class Strategy(object):
  def __init__(self, name, random_dance_generator, scoring):
    self.name = name
    self._random_dance_generator = random_dance_generator
    self._scoring = scoring
    self.best_candidate = None

  def startup(self):
    """Override to do some start-up actions such as priming the population"""
    pass

  def iterate(self):
    """Override this to do work"""
    pass

  def get_settings(self):
    return {'Strategy': self.name}

  def get_stats(self):
    # best score, mean, std dev
    return self.best_candidate.scores.total_score, self.best_candidate.scores.total_score, 0

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
    if self.best_candidate is None or candidate.scores.total_score > self.best_candidate.scores.total_score:
      self.best_candidate = candidate
