import json

with open("config.json") as json_file:
	json_data = json.load(json_file)

	TIME_INTERVAL = json_data["TIME_INTERVAL"]
	POSITION_THRESHOLD = json_data["POSITION_THRESHOLD"]
	MAX_SPEED = json_data["MAX_SPEED"]
	MAX_ROTATION = json_data["MAX_ROTATION"]
	ROTATION_THRESHOLD = json_data["ROTATION_THRESHOLD"]
	OWN_ANGLE = json_data["OWN_ANGLE"]
	OWN_ANGLE_THRESHOLD = json_data["OWN_ANGLE_THRESHOLD"]

	json_file.close()