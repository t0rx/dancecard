# Session generator

def get_possible_sessions(num_people, num_cars):
  pairs = get_pairs(num_people)
  num_pairs = len(pairs)
  indices = [0 for i in range(num_cars)]
  sessions = []
  while True:
    i = 0
    while i < num_cars:
      indices[i] = (indices[i] + 1) % num_pairs
      if indices[i] != 0:
        break
      i = i + 1
    if i == num_cars:
      break
    session = [pairs[i] for i in indices]
    if is_valid_session(session, num_people):
      sessions.append(session)
  return sessions

def is_valid_session(session, num_people):
  people = [False] * num_people
  for a, b in session:
    if people[a] or people[b]:
      return False
    people[a] = True
    people[b] = True
  return True

def get_pairs(n):
  all_combs = [[i, j] for i in range(n) for j in range(n) if i != j]
  pairs = []
  for i in all_combs:
    p = sorted(i)
    if p not in pairs:
      pairs.append(p)
  return pairs
