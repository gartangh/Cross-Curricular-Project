import math
import time
import serial
import json
import sys
#import syslog
import os
#import matplotlib
#matplotlib.use('Agg')

#import numpy as np
#import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt

from pypozyx import *

# Global variables
mayPublish = False
room = None
pos_x = None
pos_y = None

# MQTT-topics
angles = "vopeulerangles"
ranges = "vop"
position = "vopposition"
setup = "vopsetup"
identify = "identify"
room = "vopanchors"

class MyMQTTClass(mqtt.Client):

    def on_message(self, userdate, message):
        
        return

    def on_message_eulerangles(self, userdate, message):
        
        return

    def on_message_quaternion(self, userdate, message):
        
        return

    def on_message_vopposition(self, userdate, message):
        # Collect the coordinates
        global pos_x
        global pos_y

        coords = message.payload.split(',')
        pos_x = float(coords[0])
        pos_y = float(coords[1])

        return

    def on_message_room(self, userdate, message):
        global room

        print "Anchors received"
        room = Room(message.payload)

        return


    def on_message_setup(self, userdate, message):
        global mayPublish
        global room

        # Get action
        msg = str(message.payload).split('\n')

        action = str(msg[0])
        msg = msg[1:]

        # Start sending data
        if action == "start":
            mayPublish = True
            print "Start sending data"
        # Stop sending data
        elif action == "stop":
            mayPublish = False
            print "Stop sending data"
        # Update the MQTT-topic names
        elif action == "setup":
            for line in msg:
                line = line.split(' ')
                if line[0] == "angles":
                    angles = str(line[1])
                elif line[0] == "ranges":
                    ranges = str(line[1])
                elif line[0] == "position":
                    position = str(line[1])
                elif line[0] == "setup":
                    setup = str(line[1])
                elif line[0] == "identify":
                    identify = str(line[1])
            print "MQTT-topic names set"
        elif action == "Tag is online!":
            print "Tag is online!"
        # Wrong message
        else:
            print "Could not understand the message!"
        return

    def on_connect(self, client,userdata,flags,rc):
        #print "Connection returned result: " + str(rc)
        return

    def on_publish(self, mqttc, obj, mid):
        #print "mid: " + str(mid)
        return

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        #print "Subscribed: " + str(mid) + " " + str(granted_qos)
        return

    def on_log(self, client, userdate, level, buf):
        #print "log: " + buf
        return

    def start(self):
        # Connect to the MQTT server
        self.connect("157.193.214.115",1883)

        # Subscribe to the topics
        self.subscribe(setup)
        self.message_callback_add(setup, MyMQTTClass.on_message_setup)
        self.subscribe(room)
        self.message_callback_add(room, MyMQTTClass.on_message_room)
        self.on_message = MyMQTTClass.on_message

        # Start MQTT-loop
        self.loop_start()

    def stop(self):
        # Stop MQTT-loop
        self.loop_stop()
        self.disconnect()

    def publish_range(self, id, timestamp, distance):
        # range = [id, timestamp, distance]
        msg = [id]
        msg.append(timestamp)
        msg.append(distance)

        pub = (','.join(str(v) for v in msg))
        # Publish the range to the ranges-topic
        self.publish(ranges,pub)

    def publish_eulerAngles(self, euler):
        # euler = [heading, roll, pitch]
        # Publish the eulerAngles to the angle-topic
	    self.publish(angles,','.join(str(v) for v in euler))

class Anchor():
    # Containerclass for anchor
    def __init__(self,id,coordinates):
        self.id = id
        self.coordinates = Coordinates()
        self.coordinates.load(coordinates)

class Room():
    # Container for the room
    def __init__(self, setup):
        
        json_data = json.loads(setup)

        self.anchors = []
        for anchor in json_data['anchors']:

            id = int("0x"+anchor['ID'],16)
            x = int(anchor['position']['x'])
            y = int(anchor['position']['y'])
            z = int(anchor['position']['z'])
            self.anchors.append(Anchor(id,[x,y,z]))
