import yaml
import paho.mqtt.client as mqtt
from output import Publisher, format_dance
from util import new_node_id, split_host_port

class MQTTClient(object):
  def __init__(self, host, port, root_topic, advertise_node=False):
    self.node_id = new_node_id()
    self.root_topic = root_topic
    self.status_topic = self.root_topic + '/' + self.node_id + '/status'

    self.client = mqtt.Client()
    if advertise_node:
      self.client.will_set(self.status_topic, 'dead', retain=True)
    print("Connecting to MQTT broker at %s:%d under topic '%s' for node %s" % (host, port, self.root_topic, self.node_id))
    self.client.connect(host, port=port)
    self.client.loop_start()
    self.client.subscribe(self.root_topic + '/#', qos=1)
    if advertise_node:
      self.publish_status('started')

  def publish_yaml(self, subtopic, data, retain=False):
    self.client.publish(self.root_topic + '/' + subtopic, yaml.dump(data), retain=retain)

  def publish_status(self, status):
    self.client.publish(self.status_topic, status, retain=True)

  def subscribe(self, subtopic, callback):
    # Callback should take a single param of the message
    simple_callback = lambda client, userdata, message: callback(message)
    self.client.message_callback_add(self.root_topic + '/' + subtopic, simple_callback)

  def stop_loop(self):
    self.client.loop_stop()

  @staticmethod
  def from_args(args, advertise_node=False):
    if args.mqtt_config:
      return MQTTClient.from_file(args.mqtt_config)
    elif args.mqtt_host:
      host, port = split_host_port(args.mqtt_host, 1883)
      root_topic = args.mqtt_topic
      return MQTTClient(host, port, root_topic, advertise_node)
    else:
      return None

  @staticmethod
  def from_file(filename, advertise_node=False):
    with open(filename) as stream:
      config = yaml.load(stream)
    host = config['host']
    port = int(config.get('port', 1883))
    root_topic = config.get('topic', 'dancecard')
    return MQTTClient(host, port, root_topic, advertise_node)


class MQTTPublisher(Publisher):
  def __init__(self, mqttClient):
    self.client = mqttClient
    self.node_id = mqttClient.node_id

  def publish(self, subtopic, data, retain=False):
    self.client.publish_yaml(self.node_id + '/' + subtopic, data, retain=retain)

  def publish_scenario(self, scenario):
    self.publish('scenario', scenario.to_dict(), retain=True)

  def publish_stats(self, count, best, mean, std_dev):
    stats = {'count': count, 'best': best, 'mean': mean, 'std_dev': std_dev}
    self.publish('stats', stats)

  def publish_best(self, best):
    data = {'score': best.scores.total_score, 'dance': format_dance(best.dance)}
    self.publish('best', data, retain=True)

  def publish_sample(self, scenario_id, sample):
    dances = [format_dance(candidate.dance) for candidate in sample]
    m = {'scenario': scenario_id, 'dances': dances}
    self.publish('sample', m, retain=True)

  def publish_settings(self, settings):
    self.publish('settings', settings, retain=True)
