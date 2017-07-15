import random
from genetic import Genetic

class IncrementalGenetic(Genetic):
  """
    Genetic algorithm which incrementally selects two fit parents as the best of n samples, creates two offspring via crossover and mutation
    and replaces two weak members of the population with the offspring.

    Parameters applicable to this strategy:
      --population N
      --mutation-rate N
      --fittest-selections N
      --weakest-selections N
  """

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

  def get_settings(self):
    result = super(IncrementalGenetic, self).get_settings()
    result['Population size'] = self.population_size
    result['Fittest selection size'] = self.fittest_selections
    result['Weakest selection size'] = self.weakest_selections
    result['Mutation rate'] = self.mutation_rate
    result['Mutation'] = self.mutate.__name__
    result['Crossover'] = self.crossover.__name__
    return result
