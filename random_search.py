from strategy import Strategy, Candidate

class RandomSearch(Strategy):
  def __init__(self, random_dance_generator, scoring):
    super(RandomSearch, self).__init__("random search", random_dance_generator, scoring)

  def iterate(self):
    """Simply randomly generate a new dance and keep track of the best"""
    dance = self.generate_dance()
    self.create_and_track_candidate(dance)
