import math
import time
import serial
import sys
import socket
import json

import numpy as np
import paho.mqtt.client as mqtt

from pypozyx import *

# MQTT-topics
topic_waypoints = "vopwaypoints1"
topic_position = "vopposition1"
topic_height = "vopheight1"

# Global variables
waypoints = []
x = None
y = None
z = None
currentTime = time.time()
timeSet = False

# Load configuration parameters
def config():
	with open("config.json") as json_file:
		json_data = json.load(json_file)

		TIME_INTERVAL = json_data["TIME_INTERVAL"]
		POSITION_THRESHOLD = json_data["POSITION_THRESHOLD"]
		MAX_SPEED = json_data["MAX_SPEED"]
		MAX_ROTATION = json_data["MAX_ROTATION"]
		ROTATION_THRESHOLD = json_data["ROTATION_THRESHOLD"]
		OWN_ANGLE = json_data["OWN_ANGLE"]

		json_file.close()

# Get waypoints
def getWaypoints():
	global waypoints
	return waypoints

# Update waypoints
def updateWaypoints(data):
	global waypoints
	waypoints = json.loads(data)["waypoints"]
	print "Updated waypoints!"

# Container for the drone position and Euler angles
class DronePosition(object):

	# Constructor
	def __init__(self):
		self.position = Coordinates()
		self.euler = EulerAngles()

	# Update position
	def update_position(self, data):
		self.position.load(data)

	# Update position angles
	def update_euler(self, data):
		self.euler.load(data, False)

	# Fly the drone
	def fly(self, waypoint):
		global currentTime
		global timeSet

		done = False
		hover = False

		speed_forward, speed_backward, speed_left, speed_right, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise = self.algo2([waypoint[0], waypoint[1], waypoint[2]])
		
		if sum([speed_forward, speed_backward, speed_left, speed_right, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise]) == 0:
			done = True
		
		if waypoint[3] > 0:
			# Wait for a while
			if not timeSet:
				# Time was not set yet
				timeSet = True
				currentTime = time.time()
				done = False
				hover = True
			else:
				# Time was already set
				if time.time() - currentTime >= waypoint[3]:
					done = True
					timeSet = False
				else:
					hover = True
					done = False

		return speed_forward, speed_backward, speed_left, speed_right, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise, hover, done

	def distance_horizontal(self, x, y, z):
		return math.sqrt((float(x) - self.position.x)**2 + (float(y) - self.position.y)**2)

	def angle(self, x, y, z):
		angle = math.atan2(float(y) - self.position.y, float(x) - self.position.x) * 180 / math.pi - self.euler.heading + 90
		if angle > 180:
			angle = angle - 360
		elif angle < -180:
			angle = angle + 360

		return angle

	# TODO Document algorithm 1
	def algo1(self, waypoint):
		x = waypoint[0]
		y = waypoint[1]
		z = waypoint[2]

		angle_fly = self.angle(x, y, z)
		distance_fly = self.distance_horizontal(x, y, z)

		if abs(angle_fly) > 180:
			angle_t = 100 * angle_fly / abs(angle_fly)
		elif abs(angle_fly) < 5:
			angle_t = 0
		else:
			angle_t = angle_fly / 180

		if distance_fly > 10000:
			speed_t = 100
		elif distance_fly < POSITION_THRESHOLD:
			speed_t = 0
			angle_t = 0
		else:
			speed_t = distance_fly / 10000

		if angle_t > TURN_THRESHOLD:
			speed_t = 0

		return [angle_t, speed_t, 0, 0, 0]

	# TODO Document algorithm 2
	# Positive axes: forward, left, up and counterclockwise
	def algo2(self, waypoint):
		delta_x = waypoint["x"] - self.position.x
		delta_y = waypoint["y"] - self.position.y
		delta_z = waypoint["z"] - self.position.z
		delta_angle = OWN_ANGLE - self.euler.heading

		# X-axis
		if abs(delta_x) <= POSITION_THRESHOLD:
			speed_forward = 0
			speed_backward = 0
		elif delta_x > 0:
			speed_forward = 1
			speed_backward = 0
		else:
			speed_forward = 0
			speed_backward = 1

		# Y-axis
		if abs(delta_y) <= POSITION_THRESHOLD:
			speed_left = 0
			speed_right = 0
		elif delta_y > 0:
			speed_left = 1
			speed_right = 0
		else:
			speed_left = 0
			speed_right = 1

		# Z-axis
		if abs(delta_z) <= POSITION_THRESHOLD:
			speed_up = 0
			speed_down = 0
		elif delta_z > 0:
			speed_up = 1
			speed_down = 0
		else:
			speed_up = 0
			speed_down = 1

		# Heading
		if abs(delta_angle) > ROTATION_THRESHOLD:
			rotate_counterclockwise = 0
			rotate_clockwise = 0
		elif angle_disortion > 0:
			rotate_counterclockwise = 1
			rotate_clockwise = 0
		else:
			rotate_counterclockwise = 0
			rotate_clockwise = 1

		return speed_forward * MAX_SPEED, speed_backward * MAX_SPEED, speed_right * MAX_SPEED, speed_left * MAX_SPEED, speed_up * MAX_SPEED, speed_down * MAX_SPEED, rotate_counterclockwise * MAX_ROTATION, rotate_clockwise * MAX_ROTATION

# MQTT class
class MyMQTTClass(mqtt.Client):

	def on_message(self, userdate, message):
		
		return

	def on_message_waypoints(self, userdate, message):

		updateWaypoints(message.payload)

		return

	def on_message_position(self, userdate, message):
		# Collect the coordinates
		global x
		global y

		coords = message.payload.split(',')
		x = float(coords[0])
		y = float(coords[1])

		return

	def on_connect(self, client, userdata, flags, rc):
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
		self.subscribe(topic_position)
		self.message_callback_add(topic_position, MyMQTTClass.on_message_position)
		self.subscribe(topic_waypoints)
		self.message_callback_add(topic_waypoints, MyMQTTClass.on_message_waypoints)
		self.on_message = MyMQTTClass.on_message

		# Start MQTT-loop
		self.loop_start()

	def stop(self):
		# Stop MQTT-loop
		self.loop_stop()
		self.disconnect()

	def publish_height(self, height):
		self.publish(height, str(height))

if __name__ == "__main__":
	# Load configuration parameters
	config()

	# Make a connection to the MQTT server
	mqttc = MyMQTTClass("client")
	if mqttc is None:
		print "Could not create an mqtt-client!"
		quit()
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

	# Create drone optimus
	optimus = DronePostition()

	# Fly the drone
	for waypoint in getWaypoints():
		print "Next waypoint:\t" + str(waypoint["x"]) + ",\t" + str(waypoint["y"]) +  ",\t" + str(waypoint["z"])

		while 1:
			print "x: " + str(optimus.position.x) + "\t-> " + str(waypoints["x"])
			print "y: " + str(optimus.position.y) + "\t-> " + str(waypoints["y"])
			print "z: " + str(optimus.position.z) + "\t-> " + str(waypoints["z"])

			# Calculate instructions
			speed_forward, speed_backward, speed_left, speed_right, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise, hover, done = optimus.fly([waypoint["x"], waypoint["y"], waypoint["z"], 5])
			
			if done:
				# Reached waypoint
				break;

			# Send instructions
			clientsocket.send([speed_forward, speed_backward, speed_left, speed_right, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise, hover])
			# Get height back
			height = clientsocket.recv(16)

			print "height: " + str(height)
			mqttc.publish_height(height)
			
			# Wait some time
			time.sleep(TIME_INTERVAL)

	print "Flight ended!"
