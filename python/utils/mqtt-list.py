#!/usr/bin/python

# Simple utility to list subtopics.  You have to hit Ctrl-C to finish.

import sys
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

if len(sys.argv) < 3:
    print("mqtt-list host[:port] topic")
    exit(1)

hostport = sys.argv[1].split(':')
host = hostport[0]
port = hostport[1] if len(hostport) > 1 else 1883
topic = sys.argv[2]

def on_message_clean(client, userdata, message):
  print(message.topic)

try:
  subscribe.callback(on_message_clean, topic + '/#', hostname=host, port=port)
except KeyboardInterrupt:
  pass