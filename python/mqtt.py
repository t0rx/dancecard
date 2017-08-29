import os
import paho.mqtt.client as mqtt
import yaml
from output import Publisher, format_dance
from util import new_node_id, split_host_port, extant_file

default_filename = 'mqtt-config.yaml'

class MQTTClient(object):
  def __init__(self, config, advertise_node=False):
    self.node_id = new_node_id()
    self.root_topic = config.root_topic
    self.status_topic = self.root_topic + '/' + self.node_id + '/status'

    self.client = mqtt.Client()
    if config.ca_certs:
      self.client.tls_set(config.ca_certs)
    if config.username:
      self.client.username_pw_set(config.username, config.password)
    if advertise_node:
      self.client.will_set(self.status_topic, 'dead', retain=True)
    print("Connecting to MQTT broker at %s:%d under topic '%s' for node %s" % (config.host, config.port, self.root_topic, self.node_id))
    self.client.connect(config.host, port=config.port)
    self.client.loop_start()
    self.client.subscribe(self.root_topic + '/#', qos=1)
    if advertise_node:
      self.publish_status('started')

  def publish(self, subtopic, data, retain=False, as_root=False):
    topic = self.root_topic if as_root else self.root_topic + '/' + self.node_id
    self.client.publish(topic + '/' + subtopic, data, qos=1, retain=retain)

  def publish_yaml(self, subtopic, data, retain=False, as_root=False):
    self.publish(subtopic, yaml.dump(data), retain=retain, as_root=as_root)

  def publish_status(self, status):
    self.client.publish(self.status_topic, status, qos=1, retain=True)

  def subscribe(self, subtopic, callback):
    # Callback should take a single param of the message
    simple_callback = lambda client, userdata, message: callback(message)
    self.client.message_callback_add(self.root_topic + '/' + subtopic, simple_callback)

  def stop_loop(self):
    self.client.loop_stop()


class MQTTConfig(object):
  def __init__(self, host=None, port=1883, root_topic='dancecard', ca_certs=None, username=None, password=None):
    self.host = host
    self.port = port
    self.root_topic = root_topic
    self.ca_certs = ca_certs
    self.username = username
    self.password = password

  def __repr__(self):
    return "MQTTConfig(host=%s, port=%d, root_topic='%s', ca_certs=%s, username=%s, password=%s)" % (repr(self.host), self.port, self.root_topic, repr(self.ca_certs), repr(self.username), repr(self.password))

  def override_from_args(self, args):
    if args.mqtt_host:
      self.host, self.port = split_host_port(args.mqtt_host, 1883)
    if args.mqtt_topic:
      self.root_topic = args.mqtt_topic
    if args.mqtt_ca_certs:
      self.ca_certs = args.mqtt_ca_certs
    if args.mqtt_username:
      self.username = args.mqtt_username
    if args.mqtt_password:
      self.password = args.mqtt_password

  def is_valid(self):
    return self.host is not None

  @staticmethod
  def add_argument_group(parser):
    mqtt_group = parser.add_argument_group('MQTT settings', 'use these arguments to connect to an MQTT broken for publication of status and control of worker nodes.  By default, dancecard will look for the presence of ' + default_filename + ' in the working directory or in /etc/dancecard.  Individual command-line arguments will override parameters loaded from a config file.')
    mqtt_group.add_argument('--mqtt-config', metavar='filename', type=extant_file, help='if specified, use this file for MQTT connection settings.')
    mqtt_group.add_argument('--mqtt-host', metavar='host[:port]', help='MQTT broker host[:port].')
    mqtt_group.add_argument('--mqtt-topic', metavar='topic', help='root topic for MQTT, below which nodes will publish state (default "dancecard").')
    mqtt_group.add_argument('--mqtt-ca-certs', metavar='dir', help='enables TLS with CA certificates from specified directory.')
    mqtt_group.add_argument('--mqtt-username', metavar='username', help='specifies optional username for broker authentication.')
    mqtt_group.add_argument('--mqtt-password', metavar='pw', help='specified optional password for broker authentication.')

  @staticmethod
  def from_args(args):
    config = MQTTConfig()
    if args.mqtt_config:
      config = MQTTConfig.from_file(args.mqtt_config)
    elif os.path.exists('./' + default_filename):
      config = MQTTConfig.from_file('./' + default_filename)
    elif os.path.exists('/etc/dancecard/' + default_filename):
      config = MQTTConfig.from_file('/etc/dancecard/' + default_filename)

    config.override_from_args(args)
    return config if config.is_valid() else None

  @staticmethod
  def from_file(filename):
    with open(filename) as stream:
      config = yaml.load(stream)
    host = config['host']
    port = int(config.get('port', 1883))
    root_topic = config.get('topic', 'dancecard')
    ca_certs = config.get('ca-certs')
    username = config.get('username')
    password = config.get('password')
    return MQTTConfig(host, port, root_topic, ca_certs, username, password)


class MQTTPublisher(Publisher):
  def __init__(self, mqttClient):
    self.client = mqttClient
    self.node_id = mqttClient.node_id

  def publish(self, subtopic, data, retain=False):
    self.client.publish_yaml(subtopic, data, retain=retain)

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
