import json

with open('Anchors_Example.json') as json_file:
    json_data = json.load(json_file)

    for anchors in json_data['anchors']:
        print "ID: " + anchors['ID'] + "\tx: " + str(anchors['position']['x']) + "\ty: " + str(anchors['position']['y']) + "\tz: " + str(anchors['position']['z'])

    json_file.close()

raw_input()
