import time

def split_host_port(hostport, defaultPort):
  if ':' in hostport:
    host, port = host.split(':')
    port = int(port)
  else:
    host = hostport
    port = defaultPort
  return host, port

def new_scenario_id():
  return 'S-' + new_id()

def new_node_id():
  return 'N-' + new_id()

def new_id():
  import string
  from time import time
  n = int(time()*10000000)
  ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-_'
  BASE = len(ALPHABET)
  s = []
  while True:
      n, r = divmod(n, BASE)
      s.append(ALPHABET[r])
      if n == 0: break
  return ''.join(reversed(s))
