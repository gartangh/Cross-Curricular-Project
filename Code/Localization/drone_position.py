#!/usr/bin/env python

import math

from pypozyx import *

class DronePosition(object): #Container for the drone position and direction

        def __init__(self):
                self.position = Coordinates()
                self.euler = EulerAngles()

        def __str__(self):
		c = self.position
		e = self.euler
                return "X= "+str(c.x)+"; Y= "+str(c.y)+"; Z= "+str(c.z) + "; HEADING: " + str(e.heading)

        def update_position(self,data):
               self.position.load(data)

        def update_euler(self,data):
                self.euler.load(data)

        def fly(self,coords):
                if len(coords) != 3:
                        raise ValueError("Invalid coordinates")
                else:
                        x = coords[0]
                        y = coords[1]
                        z = coords[2]

                        X = self.position.x
                        Y = self.position.y
                        Z = self.position.z

                        #bereken verschil van de richting van de drone en de richting van het volgende coordinaat
                	angle_fly = self.angle(x,y,z)
        		distance_fly = self.distance_horizontal(x,y,z)
        		
        		#Draai dit verschil
                        #print("fly to: " + str(x)+", "+str(y)+", "+str(z))
                        print("Rotate " + str(angle_fly) + " degrees and fly " + str(distance_fly) + " mm.")
                        
                        return str(angle_fly)+" "+str(distance_fly) #angle distance

	def distance_horizontal(self,x,y,z):
                X = float(self.position.x)
                Y = float(self.position.y)
		return math.sqrt((float(y)-Y)**2 + (float(x)-X)**2)

	def angle(self, x,y,z):
                X = float(self.position.x)
                Y = float(self.position.y)
		error = 0
                angle = float(math.atan2(float(x)-X,Y-float(y))*180/math.pi) + error  - float(self.euler.heading)

                if angle > 180:
                        angle = angle - 360
                elif angle < -180:
                        angle = angle + 360
                
                return angle
