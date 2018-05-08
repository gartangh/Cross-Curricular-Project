#!/usr/bin/env python
import time
import serial
import time, sys, math
import paho.mqtt.client as mqtt

from pypozyx import *


from mqtt_client import * 
from drone_position import *
from init_var import *

import socket


import json


coorlijst = []


if __name__ == "__main__":
    
    mqttc = MyMQTTClass("robbe")
    mqttc.start()
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 8124))


    while(len(getCoorlijst())==0):
        print('__waiting for waypoints__')
        time.sleep(1)
        print str(len(getCoorlijst()))
        print getCoorlijst()


# # Start
#     heading_start = float(optimus.euler.heading) 
#     x_start = float(optimus.position.x)
#     y_start = float(optimus.position.y)

#     # Only when the it's not movind
#     steady = 0
#     while steady < 10:
#         if heading_start == optimus.euler.heading:
#             steady += 1
#         else:
#             heading_start = optimus.euler.heading
#             steady = 0

#     # FLY
#     init_send = ("0 " +  str(float(0.5) * float(maxrotation)) + " 0 0 0 0") 
#     print "calibrating"
#     print "init_send " + init_send 
#     clientsocket.send(init_send)
#     buff = clientsocket.recv(12)
#     time.sleep(5)
#     #Stop
    
    

#     x_stop = float(optimus.position.x)
#     y_stop = float(optimus.position.y)

#     # Calculations
#     diff = math.atan2(y_start-y_stop,x_stop-x_start) * 180 / math.pi
#     hoek =  heading_start + diff
#     print "dif " + str(diff)
#     print "eigenhoek: " + str(hoek)     
#     init_send_2 =  str(float(0) * float(maxrotation)) + " " + str(float(0) * float(maxspeed)) + " " + str(float(0) * float(maxspeed)) + " " + str(float(0) * float(maxspeed)) + " " + str(float(0) * float(maxspeed)) + " " + str(1)
#     print "hovering"
#     print "init_send2 " + init_send_2 
#     clientsocket.send(init_send_2)
#     buff = clientsocket.recv(12)
#     time.sleep(4)
    
    Time = time.time()
    hoek = EIGEN_ANGLE
    for coors in getCoorlijst():
        while(1):
            text = optimus.fly([coors[0],coors[1],coors[2],0],hoek)
            if(int(text[0])==1):
                break;
            print 'x: ' + str(float(coors[0])-float(optimus.position.x))
            print 'y: ' + str(float(coors[1])-float(optimus.position.y))
            print 'optimus: ' + str(optimus.position.x) + ' ' + str(optimus.position.y)
            # print 'goal: ' + coors[0] + ' ' + coors[1]
            print text
            send = text[1]
            clientsocket.send(send)
            buff = clientsocket.recv(12)

            if len(buff)>0:
                #print len(buff)
                print buff
            print "height: " + str(buff)
            mqttc.publish("vopheight1",buff)
            time.sleep(TIME_INTERVAL)
            print "Loop time: " + str(time.time() - Time)
            Time = time.time()


def getCoorlijst():
    global coorlijst
    return coorlijst

def updateCoorlijst(data):
    global coorlijst
    coorlijst = []
    print data
    json_data = json.loads(str(data))
    i=0
    for waypoint in json_data['waypoints']:
        coorlijst.append([0,0,0])
        coorlijst[i][0] = waypoint['position']['x']
        coorlijst[i][1] = waypoint['position']['y']
        coorlijst[i][2] = waypoint['position']['z']
        i = i+1
    print 'coorlijst updated: ' + str(coorlijst)
