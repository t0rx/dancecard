import argparse
import os
import time

def split_host_port(hostport, defaultPort):
  if ':' in hostport:
    host, port = hostport.split(':')
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

def extant_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.exists(x):
        raise argparse.ArgumentTypeError('file "{0}" does not exist'.format(x))
    return x

def hyphen_to_underscore(map):
  return {k.replace('-', '_'): v for k, v in map.items()}

class MapNamespace(object):
  """
  Allows a map to be used like a namespace, but returns None for missing names.
  """
  def __init__(self, map):
    self.map = map.copy()

  def __getattr__(self, name):
    return self.map.get(name)

  def __iter__(self):
    return self.map.__iter__()

  def merge(self, map, allow_nones=False):
    if not allow_nones:
      map = {k: v for k, v in map.items() if v is not None}
    self.map.update(map)

  def __repr__(self):
    return 'MapNamespace(%s)' % self.map