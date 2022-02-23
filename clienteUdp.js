// -------------------- udp client ----------------
var udp = require('dgram');

var buffer = require('buffer');

// creating a client socket
var client = udp.createSocket('udp4');
var PORT  = "7001"
var IP = "234.47.47.47"
//buffer msg
var data = Buffer.from('siddheshrane');

client.on('message',function(msg,info){
  console.log('Data received from server : ' + msg.toString());
  console.log('Received %d bytes from %s:%d\n',msg.length, info.address, info.port);
});

//sending msg
client.send(data,PORT,IP,function(error){
  if(error){
    client.close();
  }else{
    console.log('Data ok !!!');
  }
});

var data1 = Buffer.from('hello');
var data2 = Buffer.from('world');


const call = (ip)=> {

     client.send([data1,data2],PORT,ip,function(error){
        if(error){
            client.close();
        }else{
            console.log('Data sent = '+ ip);
        }
        })
}

//sending multiple msg

for(let i = 1; i < 255;i++)  {
    ip = `234.${i}.${i}.${i}`
    // console.log('ip '+ ip);
    call(ip)
}
