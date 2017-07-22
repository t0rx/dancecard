import random
import math
from strategy import Strategy, Candidate
from output import format_dance

class Genetic(Strategy):
  def __init__(self, name, population_size, random_dance_generator, scoring):
    super(Genetic, self).__init__(name, random_dance_generator, scoring)
    self.population_size = population_size

  def startup(self):
    self.population = self.generate_population()    # List of candidates
    scores = [c.scores.total_score for c in self.population]
    self.sumn = sum(scores)
    self.sumn2 = sum([x * x for x in scores])

  def iterate(self):
    pass

  def import_dance(self, dance):
    index = self.find_worst_index(5)
    self.replace(index, dance)

  def get_sample(self, size):
    # Just use best-of-3 to make more likely to choose better ones
    return [self.best_candidate] + [self.population[self.find_best_index(3)] for i in range(size)]

  def replace(self, index, new_dance):
    old_candidate = self.population[index]
    new_candidate = self.create_and_track_candidate(new_dance)
    self.population[index] = new_candidate

    # Update stats
    self.sumn = self.sumn - old_candidate.scores.total_score + new_candidate.scores.total_score
    self.sumn2 = self.sumn2 - (old_candidate.scores.total_score * old_candidate.scores.total_score) + (new_candidate.scores.total_score * new_candidate.scores.total_score)

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
    mean = self.sumn / self.population_size
    var = (self.sumn2 - (self.sumn * self.sumn / self.population_size)) / (self.population_size - 1)
    std_dev = math.sqrt(var)
    return self.best_candidate.scores.total_score, mean, std_dev

  def find_best_index(self, num_selections):
    """Finds the fittest amongst a sample of n"""
    best_index = -1
    best_scores = None
    for i in range(num_selections):
      index = random.randrange(self.population_size)
      scores = self.population[index].scores
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
      scores = self.population[index].scores
      if best_index == -1 or scores.total_score < best_scores.total_score:
        best_index = index
        best_scores = scores
    return best_index

  def generate_population(self):
    print("Generating initial population of size %s" % self.population_size)
    return [self.create_and_track_candidate(self.generate_dance()) for i in range(self.population_size)]

