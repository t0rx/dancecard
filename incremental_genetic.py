import random
from genetic import Genetic

class IncrementalGenetic(Genetic):
  def __init__(self, command_args, random_dance_generator, scoring):
    super(IncrementalGenetic, self).__init__("incremental genetic", command_args.population, random_dance_generator, scoring)

    self.mutation_rate = command_args.mutation_rate
    self.fittest_selections = command_args.fittest_selections
    self.weakest_selections = command_args.weakest_selections

    # Select strategies
    #self.crossover = self.crossover_single_gene
    self.crossover = self.crossover_gene_range
    #self.crossover = self.crossover_random_genes
    #self.mutate = self.mutate_single_gene
    self.mutate = self.mutate_gene_range

  def iterate(self):
    parent1 = self.find_best_index(self.fittest_selections)
    parent2 = self.find_best_index(self.fittest_selections)
    
    child1, child2 = self.crossover(self.population[parent1].dance, self.population[parent2].dance)
    if random.randrange(self.mutation_rate) == 0:
      child1 = self.mutate(child1)
    if random.randrange(self.mutation_rate) == 0:
      child2 = self.mutate(child2)

    reject_index1 = self.find_worst_index(self.weakest_selections)
    self.replace(reject_index1, child1)

    reject_index2 = self.find_worst_index(self.weakest_selections)
    self.replace(reject_index2, child2)

  def print_settings(self, file):
    super(IncrementalGenetic, self).print_settings(file)
    print("Population size=%d" % self.population_size, file=file)
    print("Fittest selection size=%d" % self.fittest_selections, file=file)
    print("Weakest selection size=%d" % self.weakest_selections, file=file)
    print("Mutation rate=%d" % self.mutation_rate, file=file)
    print("Mutation=%s" % self.mutate, file=file)
    print("Crossover=%s" % self.crossover, file=file)
    print(file=file)
