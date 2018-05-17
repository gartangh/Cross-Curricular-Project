#!/usr/bin/env python

import time
import numpy as np
import paho.mqtt.client as mqtt
import syslog
import time, sys, math
import random
import os
import json

position = "testP"
waypoints = "vopwaypoints1"
setup = "vopsetup1"
anchors = "vopanchors1"

class MyMQTTClass(mqtt.Client):

    def start(self):
        # Connect to the MQTT server
        self.connect("157.193.214.115",1883)
        # Start MQTT-loop
        self.loop_start()

    def stop(self):
        # Stop MQTT-loop
        self.loop_stop()
        self.disconnect()

if __name__ == "__main__":

    # Make a connection to the MQTT server
    mqttc = MyMQTTClass("testing")
    if mqttc is None:
        print "Could not create an mqtt-client!"
        quit()
    mqttc.start()
    time.sleep(2)

    # Publish anchors
   
    data = str(os.path.join("..","Resources","Anchors.json"))
    with open(data) as json_file:
        mqttc.publish(anchors, json.dumps(json.load(json_file)))
        json_file.close

    print "Send anchor Points"

    # Publish start
    print "send start"
    mqttc.publish(setup,"start")

    mqttc.stop()

