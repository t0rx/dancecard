import random
import math
from strategy import Strategy, Candidate
from output import format_dance

class Genetic(Strategy):
  def __init__(self, name, population_size, random_dance_generator, scoring):
    super(Genetic, self).__init__(name, random_dance_generator, scoring)
    self.population_size = population_size

  def startup(self):
    self._population = [None] * self.population_size
    self.n = 0
    self.sumn = 0
    self.sumn2 = 0

    # Create one candidate up-front to initialise best scores
    self.get_candidate(0)

  def iterate(self):
    pass

  def import_dance(self, dance):
    index = self.find_worst_index(5)
    self.replace(index, dance)

  def get_candidate(self, index):
    candidate = self._population[index]
    if not candidate:
      candidate = self.replace(index, self.generate_dance())
    return candidate

  def get_sample(self, size):
    # Just use best-of-3 to make more likely to choose better ones
    return [self.best_candidate] + [self.get_candidate(self.find_best_index(3)) for i in range(size - 1)]

  def replace(self, index, new_dance):
    old_candidate = self._population[index]
    new_candidate = self.create_and_track_candidate(new_dance)
    self._population[index] = new_candidate

    # Update stats
    if old_candidate:
      self.sumn = self.sumn - old_candidate.scores.total_score
      self.sumn2 = self.sumn2 - (old_candidate.scores.total_score * old_candidate.scores.total_score)
    else:
      self.n = self.n + 1
    self.sumn = self.sumn + new_candidate.scores.total_score
    self.sumn2 = self.sumn2 + (new_candidate.scores.total_score * new_candidate.scores.total_score)
    return new_candidate

  def crossover_single_gene(self, dance1, dance2):
    """Creates two children by switching a single gene between the parents"""
    index = random.randrange(len(dance1))
    child1 = dance1[: index] + dance2[index : index + 1] + dance1[index+1 :]
    child2 = dance2[: index] + dance1[index : index + 1] + dance2[index+1 :]
    return child1, child2

  def crossover_gene_range(self, dance1, dance2):
    """Creates two children by switching a set of genes between the parents"""
    index1 = random.randrange(len(dance1))
    index2 = index1 + random.randrange(len(dance1) - index1)
    child1 = dance1[: index1] + dance2[index1 : index2] + dance1[index2 :]
    child2 = dance2[: index1] + dance1[index1 : index2] + dance2[index2 :]
    return child1, child2

  def crossover_random_genes(self, dance1, dance2):
    """Creates two children by randomly selecting between the parents for each gene"""
    dance_size = len(dance1)
    bitmask = random.getrandbits(dance_size)
    child1=[None] * dance_size
    child2=[None] * dance_size
    for i in range(dance_size):
      if bitmask & 1 == 0:
        child1[i] = dance1[i]
        child2[i] = dance2[i]
      else:
        child1[i] = dance2[i]
        child2[i] = dance1[i]
      bitmask = bitmask >> 1
    return child1, child2

  def mutate_single_gene(self, dance):
    random_dance = self.random_dance_generator()
    child1, child2 = self.crossover_single_gene(dance, random_dance)
    return child1

  def mutate_gene_range(self, dance):
    random_dance = self.generate_dance()
    child1, child2 = self.crossover_gene_range(dance, random_dance)
    return child1

  def get_stats(self):
    # best score, mean, std dev
    mean = self.sumn / self.n
    var = (self.sumn2 - (self.sumn * self.sumn / self.n)) / (self.n - 1) if self.n > 1 else 0
    std_dev = math.sqrt(var)
    return self.best_candidate.scores.total_score, mean, std_dev

  def find_best_index(self, num_selections):
    """Finds the fittest amongst a sample of n"""
    best_index = -1
    best_scores = None
    for i in range(num_selections):
      index = random.randrange(self.population_size)
      scores = self.get_candidate(index).scores
      if best_index == -1 or scores.total_score > best_scores.total_score:
        best_index = index
        best_scores = scores
    return best_index

  def find_worst_index(self, num_selections):
    """Finds the least fit amongst a sample of n"""
    best_index = -1
    best_scores = None
    for i in range(num_selections):
      index = random.randrange(self.population_size)
      scores = self.get_candidate(index).scores
      if best_index == -1 or scores.total_score < best_scores.total_score:
        best_index = index
        best_scores = scores
    return best_index
