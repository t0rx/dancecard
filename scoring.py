# Scoring of dances

car_distribution_weight = 3

class Scores:
  """Simple holder for the various stats"""
  def __init__(self, dance, car_distances, people_distances, car_balances, people_car_matrix):
    self.dance = dance    
    self.car_distances = car_distances
    self.people_distances = people_distances
    self.car_balances = car_balances
    self.people_car_matrix = people_car_matrix
    self.total_score = sum(car_distances) + sum(people_distances) + sum(car_balances)

class Scoring:
  def __init__(self, num_cars, num_people, num_sessions):
    self.num_cars = num_cars
    self.num_people = num_people
    self.num_sessions = num_sessions
    self.car_distance_weights = [0, -5] + list(range(1, num_sessions))
    self.people_distance_weights = [0, -5] + list(range(1, num_sessions))

  def score(self, d):
    car_distances = self.dance_car_distance(d)
    people_distances = self.dance_people_distance(d)
    car_balances, people_car_matrix = self.people_car_matrix(d)
    return Scores(d, car_distances, people_distances, car_balances, people_car_matrix)

  def dance_car_distance(self, d):
    people_cars = [[-1] * self.num_cars for i in range(self.num_people)]
    scores = [0] * self.num_people
    for i in range(self.num_sessions):
      session = d[i]
      for car in range(self.num_cars):
        a, b = session[car]
        last_session_num = people_cars[a]
        scores[a] = scores[a] + self.car_distance_weights[i - last_session_num[car]]
        last_session_num[car] = i

        last_session_num = people_cars[b]
        scores[b] = scores[b] + self.car_distance_weights[i - last_session_num[car]]
        last_session_num[car] = i
    return scores

  def dance_people_distance(self, d):
    people_people = [[-1] * self.num_people for i in range(self.num_people)]
    scores = [0] * self.num_people
    for i in range(self.num_sessions):
      session = d[i]
      for car in range(self.num_cars):
        a, b = session[car]
        last_people_num = people_people[a]
        scores[a] = scores[a] + self.people_distance_weights[i - last_people_num[b]]
        last_people_num[b] = i

        last_people_num = people_people[b]
        scores[b] = scores[b] + self.people_distance_weights[i - last_people_num[a]]
        last_people_num[b] = i
    return scores

  def people_car_matrix(self, d):
    people_cars = [[0] * self.num_people for i in range(self.num_cars)]
    for session in d:
      for car in range(self.num_cars):
        a, b = session[car]
        people_cars[car][a] = people_cars[car][a] + 1
        people_cars[car][b] = people_cars[car][b] + 1
    
    factor = self.num_sessions / self.num_cars
    scores = [car_distribution_weight / factor] * self.num_people  
    for people in people_cars:
      for i in range(self.num_people):
        scores[i] = scores[i] * people[i]

    return scores, people_cars
    