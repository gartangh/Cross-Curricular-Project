import json

with open('example_waypoints.json') as json_file:
    json_data = json.load(json_file)

    for waypoint in json_data['waypoints']:
        print "ID: " + str(waypoint['ID']) + "\tx: " + str(waypoint['position']['x']) + "\ty: " + str(waypoint['position']['y']) + "\tz: " + str(waypoint['position']['z'])

    json_file.close()

raw_input()