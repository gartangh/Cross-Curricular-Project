import math
import time
import serial
import sys
import socket
import json
import paho.mqtt.client as mqtt

from drone_position import *

from pypozyx import *
#from mqtt_client import *
from pozyx_tag import *

waypoints = []

# Get waypoints
def getWaypoints():
	global waypoints
	return waypoints

# Update waypoints
def updateWaypoints(data):
	global waypoints
	waypoints = json.loads(data)["waypoints"]
	print "Updated waypoints!"

if __name__ == "__main__":
	# Set up MQTT client
	mqttc = MyMQTTClass("client")
	mqttc.start()

	# Open a socket on localhost with port 8124
	clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientsocket.connect(("localhost", 8124))

	if len(getWaypoints()) == 0:
		print "Waiting for waypoints ..."
		
		while (len(getWaypoints()) == 0):
			# Poll every second
			time.sleep(1)

		print "Got waypoints!"

	for waypoint in getWaypoints():
		while 1:
			result = optimus.fly([waypoint["x"], waypoint["y"], waypoint["z"], 0])
			
			if int(result[0]) == 1:
				# Stop the program
				break;

			print "x: " + str(waypoints["x"]) + "\t-> " + str(optimus.position.x) + "\ty: " + str(waypoints["y"]) + "\t-> " + str(optimus.position.y)

			send = result[1]
			clientsocket.send(send)
			buff = clientsocket.recv(12)

			if len(buff) > 0:
				print buff

			print "height: " + str(buff)

			mqttc.publish("vopheight1", buff)
			time.sleep(TIME_INTERVAL)
