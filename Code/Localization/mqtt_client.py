#!/usr/bin/python

import time
import paho.mqtt.client as mqtt

class MyMQTTClass(mqtt.Client):

    def on_connect(self, client,userdata,flags,rc):
	print "Connection returned result: " + str(rc)

    def on_publish(self, mqttc, obj, mid):
        print "mid: " + str(mid)

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print "Subscribed: " + str(mid) + " " + str(granted_qos)

    def on_log(self, client, userdate, level, buf):
	print "log: " + buf

    def start(self):
        self.connect("157.193.214.115",1883)
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

    def publish_eulerAngles(self, euler):
        # euler = [heading, roll, pitch]
	self.publish("vopeulerangles",','.join(str(v) for v in euler))

    def publish_quaternion(self, quat):
        # quat = [w, x, y, z]
        quat = quat[-1:] + quat[:-1] # [x, y, z, w]
	self.publish("vopquaternion",','.join(str(v) for v in quat))
