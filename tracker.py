import sys
import threading
import yaml
from time import sleep

class State(object):
  """Mutuble object to hold current state"""
  def __init__(self):
    self.active_scenario = {}
    self.nodes = {}

  def print(self):
    if self.active_scenario:
      print('Active scenario: %s' % str(self.active_scenario))
    else:
      print('Active scenario: None')
    
    for id in sorted(self.nodes.keys()):
      node = self.nodes[id]
      if node.status == 'active':
        print('Node %s: %s' % (node.id, node.stats))
      elif node.status != 'dead':
        print('Node %s: %s' % (node.id, node.status))

  def node(self, id):
    n = self.nodes.get(id)
    if not n:   # Not using setdefault because don't want to construct a Node each time we call it
      n = Node(id)
      self.nodes[id] = n
    return n

class Node(object):
  def __init__(self, id):
    self.id = id
    self.status = 'unknown'
    self.stats = {}

class Tracker(object):
  def __init__(self, mqtt_client, initial_pause):
    self.mqtt_client = mqtt_client
    self.initial_pause = initial_pause
    self.state = State()
    self.lock = threading.RLock()

  def listen(self):
    self.mqtt_client.subscribe('#', self._received_message)
    sleep(self.initial_pause)

  def print(self):
    self.state.print()

  def _received_message(self, message):
    topic = message.topic
    payload = message.payload
    #print('Received %s: %s' % (topic, payload))

    if not topic.startswith(self.mqtt_client.root_topic):
      print('ERROR: received message on topic "%s" which is not under "%s".  Ignoring.' % (topic, self.mqtt_client.root_topic), file=sys.stderr)
      return

    topic = topic[len(self.mqtt_client.root_topic) + 1 : ]
    if topic == 'control/active_scenario':
      data = decode_yaml(message.payload, topic)
      self.state.active_scenario = data
    elif topic.startswith('N-'):
      #print('Node topic %s' % topic)
      node_id = topic.split('/')[0]
      subtopic = topic[len(node_id) + 1 : ]
      node = self.state.node(node_id)
      if subtopic == 'status':
        node.status = message.payload.decode()
      elif subtopic == 'stats':
        node.stats = decode_yaml(message.payload, topic)
      else:
        # Ignore
        pass
    else:
      # Just ignore it
      pass


def decode_yaml(data, topic):
  try:
    obj = yaml.safe_load(data)
    return obj  
  except Exception as e:
    print("Exception decoding payload on topic %s.  Ignoring.  Exception: %s" % (topic, str(e)), file=sys.stderr)
    return None
