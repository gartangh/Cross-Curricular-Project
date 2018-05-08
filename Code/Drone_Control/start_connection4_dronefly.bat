:: Start the node.js server
start cmd /k node server_js_drone.js

:: Take control over the drone
start cmd /k python2 drone_localize.py
