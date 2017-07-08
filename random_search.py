from strategy import Strategy

class RandomSearch(Strategy):
  def __init__(self, random_dance_generator, scoring):
    super(RandomSearch, self).__init__("random search", random_dance_generator, scoring)

  def iterate(self):
    """Simply randomly generate a new dance"""
    scores = self.generate_and_score()
