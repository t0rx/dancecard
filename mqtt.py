import yaml
import paho.mqtt.client as mqtt
from output import Publisher, format_dance
from util import new_node_id, split_host_port

class MQTTClient(object):
  def __init__(self, args):
    self.node_id = new_node_id()
    self.root_topic = args.mqtt_topic
    status_topic = self.root_topic + '/' + self.node_id + '/status'

    self.client = mqtt.Client()
    host, port = split_host_port(args.mqtt_host, 1883)
    self.client.will_set(status_topic, 'dead', retain=True)
    print("Connecting to MQTT broker at %s:%d under topic '%s' for node %s" % (host, port, self.root_topic, self.node_id))
    self.client.connect(host, port=port)
    self.client.loop_start()
    self.client.subscribe(self.root_topic + '/#', qos=1)
    self.client.publish(status_topic, 'alive', retain=True)

  def publishYaml(self, subtopic, data, retain=False):
    self.client.publish(self.root_topic + '/' + subtopic, yaml.dump(data), retain=retain)

  def subscribe(self, subtopic, callback):
    self.client.message_callback_add(self.root_topic + '/' + subtopic, lambda client, userdata, message: callback(message))

  def stop_loop(self):
    self.client.loop_stop()


class MQTTPublisher(Publisher):
  def __init__(self, mqttClient):
    self.client = mqttClient
    self.node_id = mqttClient.node_id

  def publish(self, subtopic, data, retain=False):
    self.client.publishYaml(self.node_id + '/' + subtopic, data, retain=retain)

  def publish_scenario(self, scenario):
    self.publish('scenario', scenario.to_dict(), retain=True)

  def publish_stats(self, count, best, mean, std_dev):
    stats = {'count': count, 'best': best, 'mean': mean, 'std_dev': std_dev}
    self.publish('stats', stats)

  def publish_best(self, best):
    data = {'score': best.scores.total_score, 'dance': format_dance(best.dance)}
    self.publish('best', data, retain=True)

  def publish_settings(self, settings):
    self.publish('settings', settings, retain=True)
