#!/usr/bin/python

# Simple utility to subscribe to mqtt

import sys
import paho.mqtt.subscribe as subscribe

if len(sys.argv) < 3:
    print("mqtt-subscribe host[:port] topic")
    exit(1)

hostport = sys.argv[1].split(':')
host = hostport[0]
port = hostport[1] if len(hostport) > 1 else 1883
topic = sys.argv[2]

def on_message_print(client, userdata, message):
  print("%s %s" % (message.topic, message.payload))

try:
  subscribe.callback(on_message_print, topic, hostname=host, port=port)
except KeyboardInterrupt:
  pass