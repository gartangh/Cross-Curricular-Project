#!/usr/bin/python

import time
import paho.mqtt.client as mqtt

from drone_position import *

optimus = DronePosition()

class MyMQTTClass(mqtt.Client):

#    def on_connect(self, client,userdata,flags,rc):
#	print "Connection returned result: " + str(rc)

    def on_message(self, client, userdate, message):
	global optimus #Drone position

	data = message.payload.split(",")
	data[2] = "1000"
	optimus.update_position(data)

#        print "POSSITION RECEIVED!" + str(optimus)

#    def on_publish(self, mqttc, obj, mid):
#        print "mid: " + str(mid)

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print "Subscribed: " + str(mid) + " " + str(granted_qos)

#    def on_log(self, client, userdate, level, buf):
#	print "log: " + buf

    def start(self):
        self.connect("157.193.214.115",1883)
	time.sleep(2)
        self.subscribe("vopposition",0)
        self.loop_start()

    def stop(self):
        self.loop_stop()
        self.disconnect()
        print "Bye"

    def publish_range(self, id, timestamp, distance):

        msg = [id]
        msg.append(timestamp)
        msg.append(distance)

        pub = (','.join(str(v) for v in msg))
        self.publish("vop",pub)

    def publish_heading(self, heading):
	self.publish("heading",heading)
