#!/usr/bin/env python
""" Localizeren van de drone """
import serial
import syslog
import time
import paho.mqtt.client as mqtt

from pypozyx import (PozyxSerial, POZYX_RANGE_PROTOCOL_FAST, POZYX_RANGE_PROTOCOL_PRECISION,
			SingleRegister, DeviceRange, POZYX_SUCCESS, POZYX_FAILURE, get_first_pozyx_serial_port)

class ReadyToRange(object):
    """Continuously performs ranging between the Pozyx and a destination and sets their LEDs"""

    def __init__(self, pozyx, destination_id, protocol=POZYX_RANGE_PROTOCOL_FAST, remote_id=None):
        self.pozyx = pozyx
        self.destination_id = destination_id
        self.remote_id = remote_id
        self.protocol = protocol

if __name__ == "__main__":
    # Assign a serial port of the Pozyx
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    remote_id = None #We gebruiken de tag aan de raspberry via usb

    destination_ids = [0x6038] #Test anker
    # destination_ids = [0x6068,0x6063,0x6035,0x602D] #11de verdieping
    # destination_ids = [0x6F10,0x6F2F,0x607B,0x6F2E] #Magazijn

    ranging_protocol = POZYX_RANGE_PROTOCOL_PRECISION   # the ranging protocol

    pozyx = PozyxSerial(serial_port)
    anchors = [0] * len(destination_ids)
    i=0
    for id in destination_ids:
	anchors[i] = ReadyToRange(pozyx, id, ranging_protocol, remote_id)
	i += 1

    #mqttc = mqtt.Client("ardiuno")
    #mqttc.connect("157.193.214.115",1883)
    #time.sleep(2)

    start = time.time()*1000
    now = time.time()
    last_time = now
    first = 1

    while True:
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
				#mqttc.publish("vop",(','.join(str(v) for v in msg)[2:].upper()))
			now = time.time()
			if now - last_time > 15:
				#mqttc.publish("identiy", "vop")
				last_time = now
			print(','.join(str(v) for v in msg))
		else: #ERROR
			error_code = SingleRegister()
			status = a.pozyx.getErrorCode(error_code)
			if status == POZYX_SUCCESS:
				print("ERROR Ranging, local %s" %
					a.pozyx.getErrorMessage(error_code))
			else:
				print("ERROR Ranging, couldn't retrieve local error")
		i+=1
	
