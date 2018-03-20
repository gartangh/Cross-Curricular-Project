#!/usr/bin/env python

import serial
import syslog
import time, sys, math
import paho.mqtt.client as mqtt

from pypozyx import (PozyxSerial, POZYX_RANGE_PROTOCOL_FAST, POZYX_RANGE_PROTOCOL_PRECISION,
			SingleRegister, DeviceRange, POZYX_SUCCESS, POZYX_FAILURE, get_first_pozyx_serial_port)

from drone_position.py import *
from uwb.py import * 

if __name__ == "__main__":

    # Assign a serial port of the Pozyx
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    destination_ids = [0x6038] #Test anker
    #destination_ids = [0x6068,0x6063,0x6035,0x602D] #11de verdieping
    #destination_ids = [0x6F10,0x6F2F,0x607B,0x6F2E] #Magazijn
 
    #route
    route = ["2812,3110,1000","3413,3110,1000",
		"3413,3725,1000","3413,4326,1000","2812,4326,1000","2214,4326,1000",
		"2214,3725,1000","2214,3110,1000"]
    #endRoute

    anchors = init_anchors(destination_ids)
    mqttc = connect_to_broker()
    mqttc.loop_start()
    start, now, last_time, first = init_time()

    mqttc.subscribe("vopposition")

    c = route.pop(0).split(",")

    while True:
	try:
                if float(optimus.distance(float(c[0]),float(c[1]),float(c[2]))) < 100 and route:
                        c = route.pop(0).split(",")
		i=0
		for id in destination_ids:
			a = anchors[i]
			device_range = DeviceRange()
			status = a.pozyx.doRanging(
				a.destination_id, device_range, a.remote_id)
			if status == POZYX_SUCCESS:
				msg = [hex(a.destination_id)]
				msg.append(device_range.timestamp)
				msg.append(device_range.distance)
			
				if(len(msg)==3):
					if first==1:
						start = start - int(msg[1])
						first = 0
					msg[1] = int(int(msg[1]) + start)
					mqttc.publish("vop",(','.join(str(v) for v in msg)[2:].upper()))
#				now = time.time()
#				if now - last_time > 15:
#					mqttc.publish("identify", "vop")
#					last_time = now
				print(','.join(str(v) for v in msg)[2:].upper())
			else: #ERROR
				error_code = SingleRegister()
				status = a.pozyx.getErrorCode(error_code)
				if status == POZYX_SUCCESS:
					print("ERROR Ranging, local %s" %
						a.pozyx.getErrorMessage(error_code))
				else:
					print("ERROR Ranging, couldn't retrieve local error")
                        now = time.time()
                        if now - last_time > 15:
                                mqttc.publish("identify", "vop")
                                last_time = now
			i+=1
#		print(str(optimus))
		optimus.fly(float(c[0]),float(c[1]),float(c[2]))

	except KeyboardInterrupt:
		mqttc.loop_stop()
		mqttc.disconnect()
		print "Bye"
		sys.exit()
