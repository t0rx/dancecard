# Utility functions for outputting stuff

def output_dance_stats(scores, num_cars):
  print(scores.score)
  print(format_dance(scores.dance, num_cars))
  print("Car distance scores:", sum(scores.car_distances), scores.car_distances)
  print("People scores:", sum(scores.people_distances), scores.people_distances)
  print("Car distribution scores:", sum(scores.car_balances), scores.car_balances)
  print(format_people_car_matrix(scores.people_car_matrix))
  print()
  
def format_people_car_matrix(m):
  return '\n'.join([' '.join([str(x) for x in car]) for car in m])

def format_dance(dance, num_cars):
  result = ''
  for i in range(num_cars):
    result = result + ' '.join([format_pair(session[i]) for session in dance]) + '\n'
  return result.strip()

def format_session(session):
  return ' '.join([format_pair(pair) for pair in session])

def format_pair(pair):
  a, b = pair
  return chr(a + 65) + chr(b + 65)
