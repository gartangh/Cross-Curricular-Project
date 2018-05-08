#!/usr/bin/env python

import time
import numpy as np
import paho.mqtt.client as mqtt
import serial
import syslog
import time, sys, math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

from pypozyx import *

position = "vopposition"
waypoints = "vopwaypoints"
anchors = "testA"

waypoints_x = []
waypoints_y = []
position_x = []
position_y = []
anchors_x = []
anchors_y = []

class MyMQTTClass(mqtt.Client):

    def on_message_vopposition(self, userdate, message):
        # Collect the coordinates
        global position_x
        global position_y

        coords = message.payload.split(',')
        position_x.append(float(coords[0]))
        position_y.append(float(coords[1]))

        return

    def on_message_vopwaypoints(self,userdate,message):
        global waypoints_x
        global waypoints_y

        print "Waypoints received"

        json_data = json.loads(message.payload)

        for waypoint in json_data['waypoints']:
            waypoints_x.append(int(waypoint['position']['x']))
            waypoints_y.append(int(waypoint['position']['y']))

    def on_message_vopanchors(self,userdate,message):
        global anchors_x
        global anchors_y

        print "Anchors received"

        json_data = json.loads(message.payload)

        for anchor in json_data['anchors']:
            anchors_x.append(int(anchor['position']['x']))
            anchors_y.append(int(anchor['position']['y']))

    def start(self):
        self.connect("157.193.214.115",1883)

        self.subscribe(position)
        self.message_callback_add(position, MyMQTTClass.on_message_vopposition)
        self.subscribe(waypoints)
        self.message_callback_add(waypoints, MyMQTTClass.on_message_vopwaypoints)
        self.subscribe(anchors)
        self.message_callback_add(anchors, MyMQTTClass.on_message_vopanchors)
        
        self.loop_start()

    def stop(self):
        self.loop_stop()
        self.disconnect()
        print "Bye"

if __name__ == "__main__":

    # Connect to MQTT-server
    mqttc = MyMQTTClass("simulator")
    if mqttc is None:
        print "Could not create an mqtt-client!"
        quit()
    mqttc.start()

    data = str(os.path.join("..","Resources","Waypoints.json"))
    with open(data) as json_file:
        json_data = json.load(json_file)

        for waypoint in json_data['waypoints']:
            waypoints_x.append(int(waypoint['position']['x']))
            waypoints_y.append(int(waypoint['position']['y']))

            print "ID: " + str(waypoint['ID']) + "\tx: " + str(waypoint['position']['x']) + "\ty: " + str(waypoint['position']['y']) + "\tz: " + str(waypoint['position']['z'])

        json_file.close()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupt received, stopping..."

            fig, ax1 = plt.subplots()

            # Size of room
            xmin = 20000
            xmax = 30200
            ymin = 0
            ymax = 10800

            # Setup grid lines, based on tiles and pilars
            tile_start_x = xmin + 340
            tile_start_y = ymin + 100
            tile_width = 600 # Width of tile (mm)

            pilar_start_x = xmin + 1475
            pilar_start_y = xmin + 100
            pilar_width = 4800 # Distance between two pilars (mm)
            
            # Setup axis
            ax1.set_xlabel("x (mm)")
            ax1.set_ylabel("y (mm)")
            ax1.set_xlim(xmin,xmax)
            ax1.set_ylim(ymin,ymax)
            ax1.invert_yaxis()
            ax1.set_aspect('equal','box')
            ax1.set_xticks(range(tile_start_x,xmax,tile_width),minor=True) # Tiles verticle
            ax1.set_xticks(range(pilar_start_x,xmax,pilar_width),minor = False) # Pilar verticle
            ax1.set_yticks(range(tile_start_y,ymax,tile_width),minor=True) # Tiles horizontal
            ax1.set_yticks(range(pilar_start_y,ymax,pilar_width),minor = False) # Pilar horizontal
            ax1.grid(which='major',ls='--',linewidth=1,axis='x')
            ax1.grid(which='minor',ls='dotted',linewidth=1)
            ax1.set_title("Flight with UWB")

            # Plot waypoints
            if waypoints_x is not None:
                radius = 150
                ax1.plot(waypoints_x,waypoints_y,'r+',markersize=5)
                for i in range(0,len(waypoints_x)):
                    ax1.add_artist(
                        plt.Circle((waypoints_x[i],waypoints_y[i]),radius,color='red',fill=False))

            # Plot actual flight coordinates
            if position_x is not None:
                ax1.plot(position_x,position_y,'g-', markersize = 5)

            # Save file
            file = str(os.path.join(".","Figures","test_position_" + time.strftime("%Y%m%d-%H%M%S") + ".png"))
            plt.savefig(file)
            plt.clf()
            plt.close()

            mqttc.stop()
            quit()

            


