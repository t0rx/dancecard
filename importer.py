import sys
import yaml
import threading
import random
from output import decode_dance

class ImportSource(object):
  def get_import(self, scenario_id):
    return None

class Sample(object):
  def __init__(self, scenario_id, dances):
    self.scenario_id = scenario_id
    self.dances = dances

class MQTTImporter(ImportSource):
  def __init__(self, mqtt_client):
    self.mqtt_client = mqtt_client
    self.samples = {}
    self.lock = threading.RLock()
    self.mqtt_client.subscribe('+/sample', self._received_message)

  def get_import(self, scenario_id):
    with self.lock:
      samples = [s for s in self.samples.values() if s.scenario_id == scenario_id]
      dances = [d for s in samples for d in s.dances]      
      if dances:
        return random.choice(dances)
      else:
        return None

  def _received_message(self, message):
    topic = message.topic
    payload = message.payload

    subtopic = topic[len(self.mqtt_client.root_topic) + 1 : ]
    node_id = subtopic.split('/')[0]

    try:
      data = yaml.safe_load(payload)
      scenario_id = data['scenario']
      dances = [decode_dance(s) for s in data['dances']]
      sample = Sample(scenario_id, dances)
      with self.lock:
        self.samples[node_id] = sample
    except Exception as e:
      print("Exception decoding payload on topic %s.  Ignoring.  Exception: %s" % (topic, str(e)), file=sys.stderr)


def decode_yaml(data, topic):
  try:
    obj = yaml.safe_load(data)
    return obj  
  except Exception as e:
    print("Exception decoding payload on topic %s.  Ignoring.  Exception: %s" % (topic, str(e)), file=sys.stderr)
    return None
