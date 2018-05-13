// Global variable height, set on 0.0 m
var height = 0.0;
// Gloabal variable take off, set on false
var takeoff = false;

// Create a drone
var arDrone = require('ar-drone');
var drone  = arDrone.createClient();
drone.animateLeds('blinkRed', 5, 2);

// Get height from drone
drone.on("navdata", function(navdata) {
	if (navdata.demo)
		height = navdata.demo.altitudeMeters;
	else
		// Default height = 1.0 m
		height = 1.0;
});

// Create a server
const net = require('net');
const server = net.createServer((client) => {
	// On client connected
	console.log("Client connected!");

	// Set data encoding (either 'ascii', 'utf8', or 'base64')
	client.setEncoding("utf8");

	// On data received
	client.on('data', function(data) {
		// Take off the drone
		if (!takeoff) {
			drone.takeoff(function(err) {
				if (err)
					console.log(err);
				else {
					takeoff = true;
					drone.animateLeds('blinkGreen', 5, 2);
					console.log("Drone toke off!");
				}
			});

			return;
		}

		if (data[8])
			// Hover in place
			drone.stop();
		else {
			drone.front(data[0]);
			drone.back(data[1]);
			drone.left(data[2]);
			drone.right(data[3]);
			drone.up(data[4]);
			drone.down(data[5]);
			drone.counterclockwise(data[6])
			drone.clockwise(data[7]);
		}
		
		// Return height
		client.write(height);
	});

	// On client disconnected
	client.on("end", () => {
		console.log("Client disconnected!");
		
		// Land the drone
		if (takeoff) {
			drone.land(function(err) {
				if (err)
					console.log(err);
				else {
					takeoff = false;
					drone.animateLeds('blinkRed', 5, 2);
					console.log("Drone landed!")
				}
			});
		}
	});
});

server.on("error", (err) => {throw err});

// Server listens to port 8124
server.listen(8124, () => {console.log("Server running ...")});
