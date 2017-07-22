#!/usr/bin/python

# Simple utility to clean (i.e. delete) nodes under a specified root.  Use with care.  Hit Ctrl-C to finish

import sys
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

if len(sys.argv) < 3:
    print("mqtt-clean host[:port] topic")
    exit(1)

hostport = sys.argv[1].split(':')
host = hostport[0]
port = hostport[1] if len(hostport) > 1 else 1883
topic = sys.argv[2]

def on_message_clean(client, userdata, message):
  print("Cleaning %s" % (message.topic))
  publish.single(message.topic, payload=None, hostname=host, port = port, retain=True)

try:
  subscribe.callback(on_message_clean, topic + '/#', hostname=host, port=port)
except KeyboardInterrupt:
  pass