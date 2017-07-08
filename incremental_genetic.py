import random
from genetic import Genetic

num_selections = 5
mutation_rate = 100

class IncrementalGenetic(Genetic):
  def __init__(self, population_size, random_dance_generator, scoring):
    super(IncrementalGenetic, self).__init__("incremental genetic", population_size, random_dance_generator, scoring)

    # Select strategies
    #self.crossover = self.crossover_single_gene
    self.crossover = self.crossover_gene_range
    #self.mutate = self.mutate_single_gene
    self.mutate = self.mutate_gene_range

  def iterate(self):
    parent1 = self.find_best_index(num_selections)
    parent2 = self.find_best_index(num_selections)
    
    child1, child2 = self.crossover(self.population[parent1].dance, self.population[parent2].dance)
    if random.randrange(mutation_rate) == 0:
      child1 = self.mutate(child1)
    if random.randrange(mutation_rate) == 0:
      child2 = self.mutate(child2)

    reject_index1 = self.find_worst_index(num_selections)
    self.replace(reject_index1, child1)

    reject_index2 = self.find_worst_index(num_selections)
    self.replace(reject_index2, child2)

  def print_settings(self, file):
    super(IncrementalGenetic, self).print_settings(file)
    print("Population size=%d" % self.population_size, file=file)
    print("Selection size=%d" % num_selections, file=file)
    print("Mutation rate=%d" % mutation_rate, file=file)
    print("Mutation=%s" % self.mutate, file=file)
    print("Crossover=%s" % self.crossover, file=file)
    print(file=file)
