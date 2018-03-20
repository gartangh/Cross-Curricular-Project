#!/usr/bin/env python

from pypozyx import *

class DronePosition(object): #Container for the drone position and direction

        def __init__(self):
                self.position = Coordinates()
                self.euler = EulerAngles()

        def __str__(self):
		c = self.position
		e = self.euler
                return "POSITION: x= "+str(c.x)+"; y= "+str(c.y)+"; z= "+str(c.z) + ". EULER: " + str(e)

        def update_position(self,data):
               self.position.load(data)

        def update_euler(self,data):
                self.euler.load(data)

#        def fly(self,x,y,z):
#                #bereken verschil van de richting van de drone en de richting van het volgende coordinaat
#		angle = float(math.atan2(y-self.y,x-self.x)*180/math.pi)
#		angle_fly = angle-self.direction
#
#		distance_fly = math.sqrt((y-self.y)**2 + (x-self.x)**2)   
#		#Draai dit verschil
#                print("fly to: " + str(x)+", "+str(y)+", "+str(z))
#                #Vlieg afstand x naar voor
#		return str(angle_fly)+" "+str(distance_fly)

#	def distance(self,x,y,z):
#		return math.sqrt((y-self.y)**2 + (x-self.x)**2)
