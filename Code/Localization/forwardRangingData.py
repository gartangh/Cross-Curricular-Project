#!/usr/bin/python
import serial
import syslog
import time
import paho.mqtt.client as mqtt

mqttc = mqtt.Client("arduino") #Client aanmaken
#mqttc.connect("10.10.129.8",1883)
#mqttc.connect("10.10.131.251",1883)
mqttc.connect("157.193.214.115",1883) #Connecteren met de server op poort 1883

ard = serial.Serial("/dev/ttySAMD",115200) #Poort van de arduino
time.sleep(2) # wait for Arduino


#f = open('workfile', 'w')
#f.write('Opgestart')

start = time.time()*1000 #tijd in ms bij start programma
now = time.time() #tijd in s 
last_time = now #tijd in s
first = 1

while True:
	msg = ard.readline().rstrip() #lees arduino uit en zorgt dat
					#witruimtes weg zijn vooraan en acheraan
 	#mqttc.publish("ranging", msg)
	sp_line = msg.split(",") #string splitsen rond de komma
	if(len(sp_line)==3): #aantal argumenten == 3
		if first == 1: #eerste keer?
			start = start - int(sp_line[1]) #start is start - timestamp
			first = 0 #vanaf nu niet meer de eerste keer
		sp_line[1] = str(int(int(sp_line[1]) + start)) #timestamp = start + timestamp
		mqttc.publish("ranging", str.join(',', sp_line)) 
			#publish naar ranging in formaat id, timestamp, distance
	now = time.time() 
	if now - last_time > 15: #als het te lang duurt, kijken of we nog verbonden zijn ofzoiets
		mqttc.publish("identify", "vop")
		last_time = now
#		f.write('Identified')

#format --> id, timestamp, distance
    

