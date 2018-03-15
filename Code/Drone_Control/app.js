var autonomy = require('ardrone-autonomy');
var mission  = autonomy.createMission();

mission.takeoff()
       .zero()       // Sets the current state as the reference
       .altitude(1)  // Climb to altitude = 1 meter
       .hover(2000)  // Hover in place for 2 second
       .land();

mission.run(function (err, result) {
    if (err) {
        console.trace("Oops, something bad happened: %s", err.message);
        mission.client().stop();
        mission.client().land();
    }
    else {
        console.log("Mission success!");
        process.exit(0);
    }
});