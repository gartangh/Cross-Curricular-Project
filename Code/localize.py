#!/usr/bin/env python
"""
Blabla
"""
import serial
import syslog
import time
import paho.mqtt.client as mqtt

from pypozyx import (PozyxSerial, POZYX_RANGE_PROTOCOL_FAST, POZYX_RANGE_PROTOCOL_PRECISION,
			SingleRegister, DeviceRange, POZYX_SUCCESS, POZYX_FAILURE, get_first_pozyx_serial_port)

class ReadyToRange(object):
    """Continuously performs ranging between the Pozyx and a destination and sets their LEDs"""

    def __init__(self, pozyx, destination_id, range_step_mm=1000, protocol=POZYX_RANGE_PROTOCOL_FAST, remote_id=None):
        self.pozyx = pozyx
        self.destination_id = destination_id
        self.range_step_mm = range_step_mm
        self.remote_id = remote_id
        self.protocol = protocol

    def setup(self):
        """Sets up both the ranging and destination Pozyx's LED configuration"""
        print("- -----------POZYX RANGING V1.1 ------------")
        print()
        print("START Ranging: ")

    def loop(self, mqtt):
        """Performs ranging and sets the LEDs accordingly"""
   
	device_range = DeviceRange() #Container for the device range data {timestamp}ms, {distance}mm, {RSS}dBm
        status = self.pozyx.doRanging( 
            self.destination_id, device_range, self.remote_id) #Do ranging and fill the container

        if status == POZYX_SUCCESS: #SUCCES
	    msg =[hex(self.destination_id)] #first element of message
	    
	    #msg = msg + str(device_range).split(", ")
	    #msg = msg + device_range.data
	    msg.append(device_range.timestamp)
	    msg.append(device_range.distance)

	    #if len(msg) == 3:
		#if first == 1:
			#start = start - int(msg[2])
			#first = 0
		#msg[2] = str(int(int(msg[2])+start))
	    mqttc.publish("vop",(','.join(str(v) for v in msg)[2:].upper()))
#	    now = time.time()
#	    if now - last_time > 15:
#		mqttc.publish("identify","vop")
#		last_time = now
	    
            print(','.join(str(v) for v in msg))

            if self.ledControl(device_range.distance) == POZYX_FAILURE:
                print("ERROR: setting (remote) leds")

        else: #ERROR
            error_code = SingleRegister()
            status = self.pozyx.getErrorCode(error_code)
            if status == POZYX_SUCCESS:
                print("ERROR Ranging, local %s" %
                      self.pozyx.getErrorMessage(error_code))
            else:
                print("ERROR Ranging, couldn't retrieve local error")

    def ledControl(self, distance):
        """Sets LEDs according to the distance between two devices"""
        status = POZYX_SUCCESS
        ids = [self.remote_id, self.destination_id]
        # set the leds of both local/remote and destination pozyx device
        for id in ids:
            status &= self.pozyx.setLed(4, (distance < range_step_mm), id)
            status &= self.pozyx.setLed(3, (distance < 2 * range_step_mm), id)
            status &= self.pozyx.setLed(2, (distance < 3 * range_step_mm), id)
            status &= self.pozyx.setLed(1, (distance < 4 * range_step_mm), id)
        return status


if __name__ == "__main__":
    # Assign a serial port of the Pozyx
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    remote_id = 0x605D           # the network ID of the remote device
    remote = False               # whether to use the given remote device for ranging
    if not remote:
        remote_id = None
	
    # destination_ids = [0x6038]	#TEST
    # destination_ids = [0x6068,0x6063,0x6035,0x602D]      # network IDs of the ranging destination
    destination_ids = [0x6F10,0x6F2F,0x607B,0x6F2E]

    # distance that separates the amount of LEDs lighting up.
    range_step_mm = 1000

    ranging_protocol = POZYX_RANGE_PROTOCOL_PRECISION   # the ranging protocol

    pozyx = PozyxSerial(serial_port)
    anchors = [0] * len(destination_ids)
    i=0
    for id in destination_ids:
	anchors[i] = ReadyToRange(pozyx, id, range_step_mm,
                     ranging_protocol, remote_id)
	i += 1

    mqttc = mqtt.Client("ardiuno")
    mqttc.connect("157.193.214.115",1883)
    time.sleep(2)

    mqttc.publish("identify","vop")

    while True:
	mqttc.subscribe("vopposition",0)
#	print("message received ", str(mqttc.payload))
	i=0
	for id in destination_ids:
		anchors[i].loop(mqtt)
		i+=1
	
