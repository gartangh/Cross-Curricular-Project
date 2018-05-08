#!/usr/bin/env python

import math

from pypozyx import *
from init_var import *
import numpy as np
import time
# start = time.time()

# time.sleep(10)  # or do something more productive

# done = time.time()
# elapsed = done - start
# print(elapsed)



maxspeed = MAX_SPEED
maxrotation = MAX_ROTATION_SPEED
currentTime = time.time()
timeSet = 0


print maxspeed
print maxrotation


class DronePosition(object):  # Container for the drone position and direction

    def __init__(self):
        self.position = Coordinates()
        self.euler = EulerAngles()

    def __str__(self):
        c = self.position
        e = self.euler
        return "X= " + str(c.x) + "; Y= " + str(c.y) + "; Z= " + str(c.z) + "; HEADING: " + str(e.heading)


    def update_position(self, data):
        self.position.load(data)

    def update_euler(self, data):
        # print 'data: ' + str(data)
        self.euler.load(data, False)
        # print 'self: ' + str(self.euler)

    def fly(self, coords,hoek):
        global currentTime
        global timeSet
        if len(coords) != 4:
            raise ValueError("Invalid coordinates")
        else:
            print "Coordinaten: " + str(coords)
            X = self.position.x
            Y = self.position.y
            Z = self.position.z

            # bereken verschil van de richting van de drone en de richting van
            # het volgende coordinaat
            

            print('test')
            print 'euler: ' + str(self.euler.heading)
            # print 'afstand: ' + str(distance_fly)
            # print 'hoek: ' + str(angle_fly)
            done = '0'
            hover = '0'
            vlieg = self.algo2([coords[0],coords[1],coords[2]],hoek)
            if(sum(vlieg))==0:
                if(coords[3] != 0):
                    if(timeSet == 0):
                        timeSet = 1
                        currentTime = time.time()
                    print "currentTime: " + str(currentTime) + "Time waiting: "  + str(time.time() - currentTime)  + "Total wait time: " + str(coords[3])
                    if(time.time() - currentTime > coords[3]):
                        done = '1'
                        timeSet = 0
                    else:
                        hover = '1'
                        done = '0'
                else:
                    done = '1'

            else:
                done = '0'

            # print 'anglefly: ' + str(angle_fly)
            print 'testmaal: ' + str(vlieg[0])
            print 'testmaal: ' + str(maxrotation)

            # print 'distance_fly: ' + str(distance_fly)
            print 'testmaal: ' + str(vlieg[1])
            print 'testmaal: ' + str(maxspeed)

            print 'vlieg: ' + str(vlieg)

            

        # Draai dit verschil
            #print("fly to: " + str(x)+", "+str(y)+", "+str(z))
            print("roro " + str(float(vlieg[0]) * float(maxrotation)) +
                  " degrees and fly " + str(float(vlieg[1]) * float(maxspeed)) + " mm.")

            # angle distance
            return [done,str(float(vlieg[0]) * float(maxrotation)) + " " + str(float(vlieg[1]) * float(maxspeed)) + " " + str(float(vlieg[2]) * float(maxspeed)) + " " + str(float(vlieg[3]) * float(maxspeed)) + " " + str(float(vlieg[4]) * float(maxspeed)) + " " + str(hover)]

    def distance_horizontal(self, x, y, z):
        X = float(self.position.x)
        Y = float(self.position.y)
        return math.sqrt((float(y) - Y)**2 + (float(x) - X)**2)

    def angle(self, x, y, z):
        X = float(self.position.x)
        Y = float(self.position.y)
        error = 90
        print 'self.euler.heading: ' + str(self.euler.heading)
        print 'arctan: ' + str(math.atan2(float(x) - X, Y - float(y)) * 180 / math.pi)
        angle = float(math.atan2(float(y) - Y, float(x) - X) *
                      180 / math.pi) + error - float(self.euler.heading)

        if angle > 180:
            angle = angle - 360
        elif angle < -180:
            angle = angle + 360

        return angle

    def algo1(self, coors):

        x = coords[0]
        y = coords[1]
        z = coords[2]


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
        return [angle_t, speed_t,   0, 0, 0]

    # stuur coordinaten: [clockwise, front, back, left, right]
    # assenstelsel positief: boven en links
    def algo2(self, coors,hoek):
        delta_x = float(coors[0]) - float(self.position.x)
        delta_y = float(coors[1]) - float(self.position.y)
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

        angle_disortion = hoek - self.euler.heading
        if abs(angle_disortion) > ANGLE_CORRECTION_THRESHOLD:
            if(abs(angle_disortion)>180):
                angle_disortion = (-1)*np.sign(angle_disortion)*(360 - abs(angle_disortion))
            if(angle_disortion) > 0:
                angular_speed = 0.2
            else:
                angular_speed = -0.2



        return [angular_speed, speed_forward, speed_backward, speed_right, speed_left]
