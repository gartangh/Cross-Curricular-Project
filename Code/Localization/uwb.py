#!/usr/bin/env python

def on_connect(client,userdata,flags,rc):
	print("Connection returned result: "+str(rc))

def on_log(client, userdate, level, buf):
	print("log: "+buf)

def on_message(client, userdate, message):
	coords = message.payload.split(",")
	optimus.update_position(float(coords[0]),float(coords[1]),float(1000))
        print "Message received: " + message.payload    

def connect_to_broker():
	mqttc = mqtt.Client("vop-tag")
	mqttc.on_connect = on_connect
	mqttc.on_message = on_message
#	mqttc.on_log = on_log
	mqttc.connect("157.193.214.115",1883)
	time.sleep(2)
	return mqttc

def init_time():
	start = time.time()*1000
	now = time.time()
	last_time = now
	first = 1	
	return start, now, last_time, first

def init_anchors(destination_ids):
	remote_id = None 
	ranging_protocol = POZYX_RANGE_PROTOCOL_PRECISION   # the ranging protocol

	pozyx = PozyxSerial(serial_port)
	anchors = [0] * len(destination_ids)
	i=0
	for id in destination_ids:
		anchors[i] = ReadyToRange(pozyx, id, ranging_protocol, remote_id)
		i += 1
	return anchors
