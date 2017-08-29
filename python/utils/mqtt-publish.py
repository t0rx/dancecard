#!/usr/bin/python

# Simple utility to publish a value to mqtt

import sys
import paho.mqtt.publish as publish

if len(sys.argv) < 4:
    print("mqtt-publish host[:port] topic value")
    exit(1)

hostport = sys.argv[1].split(':')
host = hostport[0]
port = hostport[1] if len(hostport) > 1 else 1883
topic = sys.argv[2]
value = sys.argv[3]

publish.single(topic, value, hostname='localhost')
