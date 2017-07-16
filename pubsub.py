import time
import yaml
import paho.mqtt.client as mqtt
from output import Publisher, format_dance

class MQTTClient(object):
  def __init__(self, args):
    host = args.mqtt_host
    port = 1883
    if ':' in host:
      host, port = host.split(':')
      port = int(port)
    node_id = newNodeId()
    self.topic = args.mqtt_topic + '/' + node_id

    self.client = mqtt.Client()
    print("Connecting to MQTT broker at %s:%d under %s" % (host, port, self.topic))
    self.client.connect(host, port=port)
    self.client.loop_start()

  def publishYaml(self, subtopic, data, retain=False):
    self.client.publish(self.topic + '/' + subtopic, yaml.dump(data), retain=retain)


class PubSub(Publisher):
  def __init__(self, mqttClient):
    self.client = mqttClient

  def publish_scenario(self, cars, people, sessions):
    data = {'cars': cars, 'people': people, 'sessiosn': sessions}
    self.client.publishYaml('scenario', data, retain=True)

  def publish_stats(self, count, best, mean, std_dev):
    stats = {'count': count, 'best': best, 'mean': mean, 'std_dev': std_dev}
    self.client.publishYaml('stats', stats)

  def publish_best(self, best):
    data = {'score': best.scores.total_score, 'dance': format_dance(best.dance)}
    self.client.publishYaml('best', data, retain=True)

  def publish_settings(self, settings):
    self.client.publishYaml('settings', settings, retain=True)


def newNodeId():
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
