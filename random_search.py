from strategy import Strategy, Candidate

class RandomSearch(Strategy):
  """
    Randomly generates a completely new dancecard each iteration.  Not advised for real use.
  """

  def __init__(self, args, random_dance_generator, scoring):
    super(RandomSearch, self).__init__("random search", random_dance_generator, scoring)
    self.last = None

  def startup(self):
    self.iterate()  # Set up initial stats


  def iterate(self):
    """Simply randomly generate a new dance and keep track of the best"""
    dance = self.generate_dance()
    self.last = self.create_and_track_candidate(dance)
    return self.last

  def get_sample(self, size):
    return [self.best_candidate] + [self.iterate() for i in range(size - 1)]
