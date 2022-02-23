var axios = require('axios');
var qs = require('qs');
const wifi = require('node-wifi');


const logar = async () => {

    var data = qs.stringify({
        'username': 'admin',
        'password': '12345678' 
      });
    var config = {
    method: 'post',
    url: 'http://192.168.10.100/wifi_login',
    headers: { 
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    data : data
    };
     
    try {
        let response =  await  axios(config)
        console.log('################# login ################# ');
        console.log(JSON.stringify(response.data));
        console.log('################# login ################# ');

    } catch (error) {
        console.log(error)
    }

    var data = qs.stringify({
        'wifimode': '1',
        'wifiname': 'AP360 ON GRID',
        'wifipassword': 'pedsolarongrid2021' 
      });
      var config = {
        method: 'post',
        url: 'http://192.168.10.100/wifi_set',
        headers: { 
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        data : data
      };
      
      try {
        let response =  await  axios(config)
        console.log('################# AP ################# ');
        console.log(JSON.stringify(response.data));
        console.log('################# AP ################# ');

    } catch (error) {
        console.log(error)
    }
 data = qs.stringify({
    'DHCP': '1',
    'domain': '1',
    'serverDomain': '10.100.33.91',
    'serverPort': '5279',
    'TxInterval': '5',
    'invertertime': '2022-02-08 08:16:13',
    'collectortime': '2022-02-08 08:16:36' 
  });
  
  config = {
    method: 'post',
    url: 'http://192.168.10.100/net_set',
    headers: { 
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    data : data
  };
  
     
    try {
        console.log('################# config ################# ');
        let response =  await  axios(config)
        console.log(JSON.stringify(response.data));
        console.log('################# config ################# ');

    } catch (error) {
    console.log(error)
    }

 config = {
    method: 'get',
    url: 'http://192.168.10.100/wifi_restart',
    headers: { }
  };
  
     
  try {
        console.log('################# restart ################# ');
        let response =  await  axios(config)
        console.log(JSON.stringify(response.data));
        console.log('################# restart ################# ');

    } catch (error) {
     console.log(error)
    }

  
}

// Initialize wifi module
// Absolutely necessary even to set interface to null
wifi.init({
  iface: null // network interface, choose a random wifi interface if set to null
});


// Scan networks
wifi.scan((error, networks) => {
  if (error) {
    console.log(error);
  } else {
    networks.forEach(network => {

        if(network.ssid.includes('HMEX')) {
            console.log(network);
            // Connect to a network

            wifi.connect({ ssid: 'HMEXXX02201203D0', password: '12345678' },  () => {
            console.log('Connected'); 
            // on windows, the callback is called even if the connection failed due to netsh limitations
            // if your software may work on windows, you should use `wifi.getCurrentConnections` to check if the connection succeeded
             //logar()
           

            })
        }
    });
  }
});
