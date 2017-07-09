Dancecard
=========

This is an algorithm to solve the "driving trip" problem:
* n cars
* 2n drivers
* s sessions
* In each session, 2 drivers pair up per car
* We want to optimise for:
  * Everyone driving each car roughly the same number of times
  * Everyone driving with everyone else evenly
  * Minimising repetition - e.g. driving same car or with same person in nearby sessions


Running the algorithm
---------------------

The simplest way is to download the source and run `./dancecard.py`.  Alternatively, you can run as a Docker image with `docker run -it --rm t0rx/dancecard`.

The algorithm outputs new high-scoring dancecards, and also a running total of key stats:
* number of iterations
* best score
* population mean
* population standard deviation


Customising the algorithm
-------------------------

At the moment, this is done in code, but will be moved to command-line options at some point.

In `dancecard.py`:
* Set the number of cars, sessions, population size through the params at the top
* Choose which algorithm in `main()`

In `incremental_genetic.py`:
* Set the number of individuals to choose each time either for the fittest to breed, or the individual to drop out of the population for the new child.
* Set the mutation rate (likelihood is reciprocal of the specified number)
* Set the strategies for crossover and mutation in the `__init__()` method
