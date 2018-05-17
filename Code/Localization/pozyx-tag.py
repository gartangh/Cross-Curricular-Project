import time
import serial
import json

import paho.mqtt.client as mqtt

from pypozyx import *

# Global variables
mayPublish = False
room = None
pos_x = None
pos_y = None

# MQTT-topics
angles = "vopeulerangles1"
ranges = "vop"
position = "vopposition"
setup = "vopsetup1"
identify = "identify"
room = "vopanchors1"

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

		global setup 
		global ranges
		global angles
		global position

		# Get action
		action = str(message.payload)

		# Start sending data
		if action == "start":
			mayPublish = True
			print "Start sending data"
		# Stop sending data
		elif action == "stop":
			mayPublish = False
			print "Stop sending data"
		elif action == "Tag is online!":
			print "Tag is online!"
		# Wrong message
		else:
			json_data = json.loads(message.payload)

			setup = str(json_data["topic_setup"])
			ranges = str(json_data["topic_ranges"])
			angles = str(json_data["topic_orientation"])
			position = str(json_data["topic_position"])

			print "MQTT-topic names set"

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

if __name__ == "__main__":

	# Assign a serial port of the Pozyx
	serial_port = get_first_pozyx_serial_port()
	if serial_port is None:
		print "No Pozyx connected. Check your USB cable or your driver!" 
		quit()
	
	# Assign the pozyx tag
	pozyx = PozyxSerial(serial_port)

	# Make a connection to the MQTT server
	mqttc = MyMQTTClass("vop-tag")
	if mqttc is None:
		print "Could not create an mqtt-client!"
		quit()
	mqttc.start()

	# Time information for publishing 
	start = time.time()*1000
	now = time.time()
	last_time = now
	first = 1
	
	# Containers for information of the tag
	euler = EulerAngles()
	device_range = DeviceRange()

	# Anchors
	data = str(os.path.join("Resources","Waypoints2.json"))
    with open(data) as json_file:
        room = Room(json.dumps(json.load(json_file)))
        json_file.close

    mayPublish = True

	mqttc.publish(identify,"vop")
	mqttc.publish(setup,"Tag is online!")

	# Continuous want to receive input from the server
	while True:
		try:
			# Identificate every 15 seconds to the server
			now = time.time()
			if now - last_time > 15:
				mqttc.publish(identify,"vop")
				mqttc.publish(setup,"Tag is online!")
				last_time = now

			# Ready to collect 

			if (mayPublish == True and room != None):
				# Calculate the Euler angles
				pozyx.getEulerAngles_deg(euler)
				mqttc.publish_eulerAngles(euler.data)

				# Choose anchors to range with
				anchors = room.anchors
				###################################
				### TO DO - Select some anchors ###
				# When you don't know the position

				###################################

				# Calculate the Ranges
				for a in anchors:
					status = pozyx.doRanging(a.id ,device_range)
					
					if status == POZYX_SUCCESS:
						id = str(hex(a.id))[2:].upper()
						ts = device_range.timestamp
						dist = device_range.distance

						if first == 1:
							start = start - int(ts)
							first = 0
						ts = str(int(int(ts) + int(start)))
									  
						mqttc.publish_range(id,ts,dist)

		except KeyboardInterrupt:
			print "Interrupt received, stopping..."
			mqttc.stop()
			quit()
