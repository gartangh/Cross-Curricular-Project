import math
import time
import serial
import sys
import socket
import json
import os
import platform

import numpy as np
import paho.mqtt.client as mqtt

from pypozyx import *

# Global variables
# Dictionary of waypoints
waypoints = None

# Coordinates in mm
x = None
y = None
z = None

# Heading and its reference in degrees
heading = None
heading_ref = None

# Current time, not yet set
currentTime = None
timeSet = False

# Configuration parameters
ID = None
IP = None
PORT = None

topic_waypoints = None
topic_position = None
topic_orientation = None
topic_height = None

TIME_INTERVAL = None
POSITION_THRESHOLD = None
MAX_SPEED = None
MAX_ROTATION = None
ROTATION_THRESHOLD = None

# Load configuration parameters
def config():
	with open("config.json") as json_file:
		json_data = json.load(json_file)

		global ID
		global IP
		global PORT

		global topic_waypoints
		global topic_position
		global topic_orientation
		global topic_height

		global TIME_INTERVAL
		global POSITION_THRESHOLD
		global MAX_SPEED
		global MAX_ROTATION
		global ROTATION_THRESHOLD

		ID = json_data["ID"]
		IP = json_data["IP"]
		PORT = json_data["PORT"]

		topic_waypoints = json_data["topic_waypoints"] + str(ID)
		topic_position = json_data["topic_position"]# + str(ID) TODO Uncomment
		topic_orientation = json_data["topic_orientation"] + str(ID)
		topic_height = json_data["topic_height"] + str(ID)

		TIME_INTERVAL = json_data["TIME_INTERVAL"]
		POSITION_THRESHOLD = json_data["POSITION_THRESHOLD"]
		MAX_SPEED = json_data["MAX_SPEED"]
		MAX_ROTATION = json_data["MAX_ROTATION"]
		ROTATION_THRESHOLD = json_data["ROTATION_THRESHOLD"]

		json_file.close()

# Get waypoints
def getWaypoints():
	global waypoints
	return waypoints

# Update waypoints
def updateWaypoints(data):
	global waypoints
	waypoints = json.loads(data)
	print "Updated waypoints!"

# Container for the drone position and Euler angles
class DronePosition:

	# Constructor
	def __init__(self):
		global z
		global heading_ref

		self.position = Coordinates()
		self.euler = EulerAngles()

		self.position.z = z
		self.euler.heading = heading_ref

	# Fly the drone
	def fly(self, waypoint_x, waypoint_y, waypoint_z, wait):
		global x
		global y
		global z
		global heading
		global currentTime
		global timeSet

		global TIME_INTERVAL
		global POSITION_THRESHOLD
		global MAX_SPEED
		global MAX_ROTATION
		global ROTATION_THRESHOLD
		global heading_ref

		# Update own orientation
		self.position.x = x
		self.position.y = y
		self.position.z = z
		self.euler.heading = heading

		done = False
		hover = False

		# Execute algorithm here
		#speed_forward, speed_backward, speed_right, speed_left, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise = self.algo1(waypoint[0], waypoint[1], waypoint[2])
		speed_forward, speed_backward, speed_right, speed_left, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise = self.algo2(waypoint_x, waypoint_y, waypoint_z)
		
		if sum([speed_forward, speed_backward, speed_right, speed_left, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise]) == 0:
			done = True
		
		if done and wait > 0:
			# Wait for a while
			if not timeSet:
				# Time was not set yet
				timeSet = True
				currentTime = time.time()
				done = False
				hover = True
			else:
				# Time was already set
				if time.time() - currentTime >= wait:
					done = True
					timeSet = False
				else:
					hover = True
					done = False

		return speed_forward * MAX_SPEED, speed_backward * MAX_SPEED, speed_right * MAX_SPEED, speed_left * MAX_SPEED, speed_up * MAX_SPEED, speed_down * MAX_SPEED, rotate_counterclockwise * MAX_ROTATION, rotate_clockwise * MAX_ROTATION, hover, done

	# Return distance from current position to waypoint in mm
	def distance_horizontal(self, waypoint_x, waypoint_y, waypoint_z):
		return math.sqrt((waypoint_x - self.position.x)**2 + (waypoint_y - self.position.y)**2)

	# Return arctan from current position to waypoint in degrees
	def angle(self, waypoint_x, waypoint_y, waypoint_z):
		# Error of 90 degrees
		return math.atan2(waypoint_y - self.position.y, waypoint_x - self.position.x) * 180 / math.pi + 90

	# Positive axes: forward, left, up and counterclockwise
	def algo1(self, waypoint_x, waypoint_y, waypoint_z):
		global POSITION_THRESHOLD
		global ROTATION_THRESHOLD
		global heading_ref

		# Default in this algorithm
		speed_backward = 0
		speed_left = 0
		speed_right = 0

		delta_distance = self.distance_horizontal(waypoint_x,waypoint_y, waypoint_z)
		delta_z = waypoint_z - self.position.z
		delta_angle = self.angle(waypoint_x, waypoint_y, waypoint_z) - self.euler.heading

		# Distance
		if abs(delta_distance) <= POSITION_THRESHOLD:
			speed_forward = 0
		elif abs(delta_distance) > 10000:
			speed_forward = 1
		else:
			speed_forward = delta_distance / 10000

		# Z-axis
		if abs(delta_z) <= POSITION_THRESHOLD:
			speed_up = 0
			speed_down = 0
		elif delta_z > 0:
			if delta_z > 10000:
				speed_up = 1
			else:
				speed_up = delta_z / 10000
			speed_down = 0
		else:
			speed_up = 0
			if delta_z < -10000:
				speed_down = 1
			else:
				speed_down = abs(delta_z) / 10000

		# Heading
		if abs(delta_angle) <= ROTATION_THRESHOLD:
			rotate_counterclockwise = 0
			rotate_clockwise = 0
		elif delta_angle > ROTATION_THRESHOLD:
			rotate_counterclockwise = 1
			rotate_clockwise = 0
			# Overwrite speed forward
			speed_forward = 0
		else:
			rotate_counterclockwise = 0
			rotate_clockwise = 1
			# Overwrite speed forward
			speed_forward = 0

		return speed_forward, speed_backward, speed_right, speed_left, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise

	# Positive axes: forward, left, up and counterclockwise
	def algo2(self, waypoint_x, waypoint_y, waypoint_z):
		global POSITION_THRESHOLD
		global ROTATION_THRESHOLD
		global heading_ref

		delta_x = waypoint_x - self.position.x
		delta_y = waypoint_y - self.position.y
		delta_z = waypoint_z - self.position.z
		delta_angle = heading_ref - self.euler.heading
		if delta_angle > 180:
			delta_angle -= 360
		elif delta_angle < -180:
			delta_angle += 360

		# X-axis
		if abs(delta_x) <= POSITION_THRESHOLD:
			speed_forward = 0
			speed_backward = 0
		elif delta_x > 0:
			if delta_x > 10000:
				speed_forward = 1
			else:
				speed_forward = float(delta_x) / 10000
			speed_backward = 0
		else:
			speed_forward = 0
			if delta_x < -10000:
				speed_backward = 1
			else:
				speed_backward = abs(float(delta_x)) / 10000

		# Y-axis
		if abs(delta_y) <= POSITION_THRESHOLD:
			speed_left = 0
			speed_right = 0
		elif delta_y > 0:
			if delta_y > 10000:
				speed_right = 1
			else:
				speed_right = float(delta_y) / 10000
			speed_left = 0
		else:
			speed_right = 0
			if delta_y < -10000:
				speed_left = 1
			else:
				speed_left = abs(float(delta_y)) / 10000

		# Z-axis
		if abs(delta_z) <= POSITION_THRESHOLD:
			speed_up = 0
			speed_down = 0
		elif delta_z > 0:
			if delta_z > 10000:
				speed_up = 1
			else:
				speed_up = float(delta_z) / 10000
			speed_down = 0
		else:
			speed_up = 0
			if delta_z < -10000:
				speed_down = 1
			else:
				speed_down = abs(float(delta_z)) / 10000

		# Heading
		if abs(delta_angle) <= ROTATION_THRESHOLD:
			rotate_counterclockwise = 0
			rotate_clockwise = 0
		elif delta_angle > 0:
			rotate_counterclockwise = 0
			rotate_clockwise = 1
		else:
			rotate_counterclockwise = 1
			rotate_clockwise = 0

		print "algo2: " + str(speed_forward), str(speed_backward), str(speed_right), str(speed_left), str(speed_up), str(speed_down), str(rotate_counterclockwise), str(rotate_clockwise)
		return speed_forward, speed_backward, speed_right, speed_left, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise

# MQTT class
class MyMQTTClass(mqtt.Client):

	def on_message_waypoints(self, userdate, message):
		updateWaypoints(message.payload)

		return

	def on_message_position(self, userdate, message):
		global x
		global y
		
		# Collect x and y coordinates
		coords = message.payload.split(",")
		x = int(float(coords[0]))
		y = int(float(coords[1]))
		# z = int(coords[2]) is to innacurate, the height from the drone sensors will be used

		return

	def on_message_euler(self, userdate, message):
		global heading_ref
		global heading

		# Collect heading
		orientation = message.payload.split(",")
		heading = int(float(orientation[0]))
		# pitch = int(orientation[1]) will not be used here
		# roll = int(orientation[2]) will not be used here

		if heading_ref == None:
			heading_ref = int(heading)

		return

	def start(self):
		# Connect to the MQTT server
		# TODO Connect via IP address of the correct interface
		self.connect(IP, port=PORT)#, bind_address="10.10.130.158")

		# Subscribe to the topics
		self.subscribe(topic_waypoints)
		self.message_callback_add(topic_waypoints, MyMQTTClass.on_message_waypoints)
		self.subscribe(topic_position)
		self.message_callback_add(topic_position, MyMQTTClass.on_message_position)
		self.subscribe(topic_orientation)
		self.message_callback_add(topic_orientation, MyMQTTClass.on_message_euler)

		# Start MQTT-loop
		self.loop_start()

	def stop(self):
		# Stop MQTT-loop
		self.loop_stop()
		self.disconnect()

	def publish_height(self, height):
		self.publish(topic_height, str(height))

if __name__ == "__main__":
	z = 1000

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

	# Create drone optimus
	optimus = DronePosition()

	# Wait for waypoints
	if getWaypoints() == None:
		print "Waiting for waypoints ..."
		
		while getWaypoints() == None:
			# Poll every second
			time.sleep(1)

		print "Got waypoints!"

	# Fly the drone
	takoff = False
	waypoints = getWaypoints()["waypoints"]
	for waypoint in waypoints:
		waypoint_ID = waypoint["ID"]
		waypoint_x = waypoint["position"]["x"]
		waypoint_y = waypoint["position"]["y"]
		waypoint_z = waypoint["position"]["z"]

		print "Next waypoint: [" + str(waypoint_ID) + "] " + str(waypoint_x) + "," + str(waypoint_y) +  "," + str(waypoint_z)
		# t1 = datetime.now()


		while True:
			#if platform.system == "Windows":
			os.system("cls")
			#elif platform.system == "Linux":
			#	os.system("clear")

			print "ID: " + str(waypoint_ID)
			print "{:>6}\t->\t{:>6}".format(x, waypoint_x)
			print "{:>6}\t->\t{:>6}".format(y, waypoint_y)
			print "{:>6}\t->\t{:>6}".format(z, waypoint_z)
			print "{:>6}\t->\t{:>6}".format(heading, heading_ref)


			# Calculate instructions and hover 0 s over the waypoint
			speed_forward, speed_backward, speed_right, speed_left, speed_up, speed_down, rotate_counterclockwise, rotate_clockwise, hover, done = optimus.fly(waypoint_x, waypoint_y, waypoint_z, 0)




			if done:
				# Reached waypoint
				break

			# Waypoint not yet reached
			# Send instructions
			if hover:
				hover_send = "1"
			else:
				hover_send = "0"

			clientsocket.send(str(speed_forward) + "," + str(speed_backward) + "," + str(speed_right) + "," + str(speed_left) + "," + str(speed_up) + "," + str(speed_down) + "," + str(rotate_counterclockwise) + "," + str(rotate_clockwise) + "," + hover_send)

			if not takoff:
				print "Ready for take off!"
				time.sleep(2)
				takoff = True
				print "Take off!"
			else:
				# Get height in mm back (read maximum 16 bytes)
				z = int(clientsocket.recv(16))
				mqttc.publish_height(z)
				
				# Wait some time before sending next instructions
				time.sleep(TIME_INTERVAL)

	print "Flight ended!"
