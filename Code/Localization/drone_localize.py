#!/usr/bin/env python

import serial
import syslog
import time, sys, math
import paho.mqtt.client as mqtt

from pypozyx import *

from mqtt_client import *

if __name__ == "__main__":
    
    # Assign a serial port of the Pozyx
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()
        
    pozyx = PozyxSerial(serial_port)

    # Make a connection to the MQTT server
    mqttc = MyMQTTClass("vop-tag")
    mqttc.start()

    # Important for the timestamps
    start = time.time()*1000
    now = time.time()
    last_time = now
    first = 1    

    #destination_ids = [0x6008] #Test anker    
    destination_ids = [0x6F10,0x6F2F,0x607B,0x6F2E] #Magazijn

    # Containers for information of the tag
    euler = EulerAngles()
    quat = Quaternion()
    device_range = DeviceRange()

    while True:
     try:
        # Identificate every 15 seconds to the server
        now = time.time()
        if now - last_time > 15:
            mqttc.publish("identify","vop")
            last_time = now

        # Calculate the Euler angles
        pozyx.getEulerAngles_deg(euler)
        mqttc.publish_eulerAngles(euler.data)

        # Calculate the Quaternions
        pozyx.getQuaternion(quat)
        mqttc.publish_quaternion(quat.data)

        # Calculate the Ranges
        for dest_id in destination_ids:
            status = pozyx.doRanging(dest_id,device_range)
            
            if status == POZYX_SUCCESS:
                id = str(hex(dest_id))[2:].upper()
                ts = device_range.timestamp
                dist = device_range.distance

                if first == 1:
                    start = start - int(ts)
                    first = 0
                ts = str(int(int(ts) + int(start)))
		print "publish"                
                mqttc.publish_range(id,ts,dist)

     except KeyboardInterrupt:
         mqttc.stop()
         sys.exit()
