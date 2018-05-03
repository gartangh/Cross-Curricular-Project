import paho.mqtt.client as mqtt
import json

# Make a connection to the MQTT server
mqttc = mqtt.Client("vopwaypoints")
if mqttc is None:
    print "Could not create an mqtt-client!"
    quit()
mqttc.connect("157.193.214.115", 1883)
mqttc.loop_start()

# Publish the JSON formatted string with all anchors
with open('Waypoints_Example.json') as json_file:
    mqttc.publish("vopwaypoints", json.dumps(json.load(json_file)))
    json_file.close()

mqttc.loop_stop()
mqttc.disconnect()