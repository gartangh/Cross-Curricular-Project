#!/usr/bin/env python

import serial
import syslog
import time, sys, math
import paho.mqtt.client as mqtt

from pypozyx import *

from mqtt_client import * 
from drone_position import *

if __name__ == "__main__":
    
    # Assign a serial port of the Pozyx
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()
        
    pozyx = PozyxSerial(serial_port)
    remote_id = None
#    pozyx.remote_id = remote_id # Uses another tag to range

    mqttc = MyMQTTClass("vop-tag")
    mqttc.start()

    start = time.time()*1000
    now = time.time()
    last_time = now
    first = 1    

    #destination_ids = [0x6038] #Test anker    
    destination_ids = [0x6F10,0x6F2F,0x607B,0x6F2E] #Magazijn
    point = [0,0,1000]

    while True:
     try:
	pozyx.getEulerAngles_deg(optimus.euler,remote_id)
	print str(optimus)
        for dest_id in destination_ids:
            now = time.time()
            if now - last_time > 15:
                mqttc.publish("identify","vop")
                last_time = now
            
            device_range = DeviceRange()
            status = pozyx.doRanging(dest_id,device_range,remote_id)
            
            if status == POZYX_SUCCESS:
                id = str(hex(dest_id))[2:].upper()
                ts = device_range.timestamp
                dist = device_range.distance

                if first == 1:
                    start = start - int(ts)
                    first = 0
                ts = str(int(int(ts) + int(start)))
                
                mqttc.publish_range(id,ts,dist)
#            else:
#                error_code = SingleRegister()
#                status = pozyx.getErrorCode(error_code)
#                if status == POZYX_SUCCESS:
#                    print "ERROR Ranging, local %s" % pozyx.getErrorMessage(error_code)
#                else:
#                    print "ERROR Ranging, couldn't retrieve local error"

#	mqttc.publish("heading",str(optimus.euler.heading))
	
	if optimus.position.x != 0:
	        optimus.fly(point)
        
     except KeyboardInterrupt:
         mqttc.stop()
         sys.exit()
