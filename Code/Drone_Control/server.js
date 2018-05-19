// Global variable height, set on 0.0 m
var height = 2.0;
// Gloabal variable take off, set on false
var takeoff = false;

// Create a drone
var arDrone = require("ar-drone");
var drone  = arDrone.createClient();
//drone.animateLeds("blinkRed", 5, 2);

// Get height from drone
drone.on("navdata", function(navdata) {
	if (navdata.demo)
		height = navdata.demo.altitude;
	else
		// Default height = 1.0 m
		height = 1.0;
});

// Create a server
const net = require("net");
const server = net.createServer((client) => {
	// On client connected
	console.log("Client connected!");

	// Set data encoding to UFT-8
	client.setEncoding("utf8");

	// On data received
	client.on("data", function(data) {
		// Take off the drone
		if (!takeoff) {
			console.log("Ready for take off!");	
			// Take off the drone
			/*
			drone.takeoff(function(err) {
-				if (err)
-					console.log(err);
-				else {
-					takeoff = true;
-					//drone.animateLeds("blinkGreen", 5, 2);
-					console.log("Take off!");
-				}
-			});
			*/
			drone.takeoff();
			takeoff = true;
			console.log("Take off!");

			return;
		}

		instructions = data.split(",");
		console.log(instructions);
		if (instructions[8] == 1)
			// Hover in place
			drone.stop();
		else {
			if (instructions[0] != 0)
				drone.front(instructions[0]);
			if (instructions[1] != 0)
				drone.back(instructions[1]);
			if (instructions[2] != 0)
				drone.right(instructions[2]);
			if (instructions[3] != 0)
				drone.left(instructions[3]);
			if (instructions[4] != 0)
				drone.up(instructions[4]);
			if (instructions[5] != 0)
				drone.down(instructions[5]);
			if (instructions[6] != 0)
				drone.counterClockwise(instructions[6]);
			if (instructions[7] != 0)
				drone.clockwise(instructions[7]);
		}
		
		// Return height in mm
		//var heightmm = Math.round(1000 * height);
		var heightmm = 1000;
		client.write(heightmm.toString());
	});

	// On client disconnected
	client.on("end", () => {
		console.log("Client disconnected!");
		
		if (takeoff) {
			console.log("Ready for touch down!");
			// Land the drone
			/*
			drone.land(function(err) {
				if (err)
					console.log(err);
				else {
					takeoff = false;
					//drone.animateLeds("blinkRed", 5, 2);
					console.log("Touch down!");
				}
			});
			*/
			drone.land();
			takeoff = false;
			console.log("Touch down!");
		}
	});
});

server.on("error", (err) => {
	throw err;
});

// Server listens to port 8124
server.listen(8124, () => {
	console.log("Server running ...");
});
