import random
import math
from strategy import Strategy
from output import format_dance

class Genetic(Strategy):
  def __init__(self, name, population_size, random_dance_generator, scoring):
    super(Genetic, self).__init__(name, random_dance_generator, scoring)
    self.population_size = population_size
    self.population = self.generate_population()    # List of dances with scores
    scores = [s.total_score for s in self.population]
    self.sumn = sum(scores)
    self.sumn2 = sum([x * x for x in scores])

  def iterate(self):
    pass

  def replace(self, index, new_dance):
    old_scores = self.population[index]
    new_scores = self.score_and_track(new_dance)
    self.population[index] = new_scores

    # Update stats
    self.sumn = self.sumn - old_scores.total_score + new_scores.total_score
    self.sumn2 = self.sumn2 - (old_scores.total_score * old_scores.total_score) + (new_scores.total_score * new_scores.total_score)

  def crossover_single_gene(self, dance1, dance2):
    """Creates two children by switching a single gene between the parents"""
    child1 = list(dance1)   # Copying so we don't modify the originals
    child2 = list(dance2)
    index = random.randrange(len(dance1))
    child1[index] = dance2[index]
    child2[index] = dance1[index]

    return child1, child2

  def mutate(self, dance):
    random_dance = self.random_dance_generator()
    gene_index = random.randrange(len(dance))
    result = list(dance)    # So we don't modify the original
    result[gene_index] = random_dance[gene_index]
    return result

  def output(self):
    super(Genetic, self).output()
    print (self.sumn, self.sumn2)
    var = (self.sumn2 - (self.sumn * self.sumn / self.population_size)) / (self.population_size - 1)
    std_dev = math.sqrt(var)
    print("Std dev: %d" % std_dev)

  def find_best_index(self, num_selections):
    """Finds the fittest amongst a sample of n"""
    best_index = -1
    best_scores = None
    for i in range(num_selections):
      index = random.randrange(self.population_size)
      scores = self.population[index]
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
      scores = self.population[index]
      if best_index == -1 or scores.total_score < best_scores.total_score:
        best_index = index
        best_scores = scores
    return best_index

  def generate_population(self):
    print("Generating initial population of size %s" % self.population_size)
    return [self.generate_and_score() for i in range(self.population_size)]

