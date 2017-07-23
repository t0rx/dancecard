import os
import paho.mqtt.client as mqtt
import yaml
from output import Publisher, format_dance
from util import new_node_id, split_host_port, extant_file

class MQTTClient(object):
  def __init__(self, config, advertise_node=False):
    self.node_id = new_node_id()
    self.root_topic = config.root_topic
    self.status_topic = self.root_topic + '/' + self.node_id + '/status'

    self.client = mqtt.Client()
    if advertise_node:
      self.client.will_set(self.status_topic, 'dead', retain=True)
    print("Connecting to MQTT broker at %s:%d under topic '%s' for node %s" % (config.host, config.port, self.root_topic, self.node_id))
    self.client.connect(config.host, port=config.port)
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


class MQTTConfig(object):
  def __init__(self, host=None, port=1883, root_topic='dancecard'):
    self.host = host
    self.port = port
    self.root_topic = root_topic

  def __repr__(self):
    return "MQTTConfig(host=%s, port=%d, root_topic='%s')" % (repr(self.host), self.port, self.root_topic)

  @staticmethod
  def add_argument_group(parser):
    mqtt_group = parser.add_argument_group('MQTT settings', 'use these arguments to connect to an MQTT broken for publication of status and control of worker nodes.  By default, dancecard will look for the presence of mqtt-config.yaml in the working directory or in /etc/dancecard.  Individual command-line arguments will override parameters loaded from a config file.')
    mqtt_group.add_argument('--mqtt-config', metavar='filename', type=extant_file, help='if specified, use this file for MQTT connection settings.')
    mqtt_group.add_argument('--mqtt-host', metavar='host[:port]', help='MQTT broker host[:port].')
    mqtt_group.add_argument('--mqtt-topic', metavar='topic', help='root topic for MQTT, below which nodes will publish state (default "dancecard")')

  @staticmethod
  def from_args(args):
    config = MQTTConfig()
    if args.mqtt_config:
      config = MQTTConfig.from_file(args.mqtt_config)
    elif os.path.exists('./mqtt-config.yaml'):
      config = MQTTConfig.from_file('./mqtt-config.yaml')
    elif os.path.exists('/etc/dancecard/mqtt-config.yaml'):
      config = MQTTConfig.from_file('/etc/dancecard/mqtt-config.yaml')

    # Override with command-line args
    if args.mqtt_host:
      config.host, config.port = split_host_port(args.mqtt_host, 1883)
    if args.mqtt_topic:
      config.root_topic = args.mqtt_topic

    if config.host:     # If no MQTT config at all then host will still be None
      return config
    else:
      return None

  @staticmethod
  def from_file(filename):
    with open(filename) as stream:
      config = yaml.load(stream)
    host = config['host']
    port = int(config.get('port', 1883))
    root_topic = config.get('topic', 'dancecard')
    return MQTTConfig(host, port, root_topic)


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
