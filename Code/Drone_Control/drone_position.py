import math
import time

import numpy as np

from config import *

from pypozyx import *

currentTime = time.time()
timeSet = False

# Container for the drone position and Euler angles
class DronePosition(object):

	# Constructor
	def __init__(self):
		self.position = Coordinates()
		self.euler = EulerAngles()

	# To string
	def __str__(self):
		return "X = " + str(self.position.x) + "\tY = " + str(self.position.y) + "\tZ = " + str(self.position.z) + "\tHEADING = " + str(self.euler.heading)

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

		if len(waypoint) != 4:
			raise ValueError("Invalid coordinates")
		else:
			# Calculate the difference between the direction of the drone and the direction of the next waitpoint
			done = False
			hover = False
			#result = self.algo1([waypoint[0], waypoint[1], waypoint[2]])
			result = self.algo2([waypoint[0], waypoint[1], waypoint[2]])
			if sum(result) == 0:
				if waypoint[3] != 0:
					if not timeSet:
						timeSet = True
						currentTime = time.time()
					print "currentTime: " + str(currentTime) + "Time waiting: "  + str(time.time() - currentTime)  + "Total wait time: " + str(waypoint[3])
					
					if time.time() - currentTime > waypoint[3]:
						done = True
						timeSet = False
					else:
						hover = True
						done = False
				else:
					done = True
			else:
				done = False

			return [done, str(float(result[0]) * float(maxrotation)) + " " + str(float(result[1]) * float(maxspeed)) + " " + str(float(result[2]) * float(maxspeed)) + " " + str(float(result[3]) * float(maxspeed)) + " " + str(float(result[4]) * float(maxspeed)) + " " + str(hover)]

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
	# Send coordinates: [clockwise, front, back, left, right]
	# Positive axes: up and left
	def algo2(self, waypoint):
		delta_x = float(waypoint[0]) - float(self.position.x)
		delta_y = float(waypoint[1]) - float(self.position.y)
		speed_forward = 0
		speed_backward = 0
		speed_left = 0
		speed_right = 0
		angular_speed = 0

		if abs(delta_x) > 10000:
			if delta_x > 0:
				speed_forward = 1
			else:
				speed_backward = 1
		elif abs(delta_x) < POSITION_THRESHOLD:
			speed_forward = 0
			speed_backward = 0
		else:
			if delta_x > 0:
				speed_forward = abs(delta_x) / 10000
			else:
				speed_backward = abs(delta_x) / 10000

		if abs(delta_y) > 10000:
			if delta_y > 0:
				speed_left = 1
			else:
				speed_right = 1
		elif abs(delta_y) < POSITION_THRESHOLD:
			speed_left = 0
		else:
			if delta_y > 0:
				speed_left = abs(delta_y) / 10000
			else:
				speed_right = abs(delta_y) / 10000

		angle_disortion = OWN_ANGLE - self.euler.heading
		if abs(angle_disortion) > OWN_ANGLE_THRESHOLD:
			if abs(angle_disortion)>180:
				angle_disortion = (-1)*np.sign(angle_disortion)*(360 - abs(angle_disortion))
			if angle_disortion > 0:
				angular_speed = 0.2
			else:
				angular_speed = -0.2

		return [angular_speed, speed_forward, speed_backward, speed_right, speed_left]
