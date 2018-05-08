var arDrone = require('ar-drone');
var client  = arDrone.createClient();
var hoogte=1.111;
var takeoff = 0;

const net = require('net');
const server = net.createServer((c) => {
  // 'connection' listener
  console.log('client connected');
  //client.takeoff();
  c.on('end', () => {
    console.log('client disconnected');
    client.land();
  });
  

  	c.setEncoding("utf8");
  
 // 	c.write('hello\r\n');
 // 	c.pipe(c);

 	
 //set data encoding (either 'ascii', 'utf8', or 'base64')
    c.on('data', function(data) {
        //console.log(data);
        if(!takeoff){
          takeoff = 1;
          client.takeoff();
        }
        var arr = data.split(" ");
        console.log(arr);
        if(arr[5] != 0) client.stop();
        else{
          if(arr[0] != 0) client.clockwise(parseFloat(arr[0]));
          if(arr[1] != 0) client.front(parseFloat(arr[1]));
          if(arr[2] != 0) client.back(parseFloat(arr[2]));
          if(arr[3] != 0) client.left(parseFloat(arr[3]));
          if(arr[4] != 0) client.right(parseFloat(arr[4]));
        }
        

        var correct = c.write(hoogte.toString());
        //c.pipe(c);
        if(correct){
        	console.log('correct');
        }
        
    });

});

client.on('navdata', function(navigation_data){
  if(navigation_data.demo){ //console.log(navigation_data.demo.altitude);
    hoogte = navigation_data.demo.altitude}
  else{
    hoogte = 0.000
  }
  
});

server.on('error', (err) => {
  throw err;
});
server.listen(8124, () => {
  console.log('server bound');
});


