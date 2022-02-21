#Grott Growatt monitor :  Proxy 
#       
# Updated: 2020-10-04
# Version 2.2.1d

import socket
import select
import time
import sys
import struct
import textwrap
from itertools import cycle # to support "cycling" the iterator
import time, json, codecs
from datetime import datetime
from rx import catch
from termcolor import colored

## to resolve errno 32: broken pipe issue (only linux)
if sys.platform != 'win32' :
   from signal import signal, SIGPIPE, SIG_DFL

from grottdata import procdata, decrypt, decryptH

#import mqtt                       
import paho.mqtt.publish as publish

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
#buffer_size = 65535
delay = 0.0002

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            print(e)
            return False  

class Proxy:
    input_list = []
    channel = {}

    def __init__(self, conf):
        print("\nGrott proxy mode started")
        ## to resolve errno 32: broken pipe issue (Linux only)
        if sys.platform != 'win32':
            signal(SIGPIPE, SIG_DFL) 
        ## 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #set default grottip address
        if conf.grottip == "default" : conf.grottip = '0.0.0.0'
        self.server.bind((conf.grottip, conf.grottport))
        #socket.gethostbyname(socket.gethostname())
        try: 
            hostname = (socket.gethostname())    
            print("Hostname :", hostname)
            print("IP : ", socket.gethostbyname(hostname), ", port : ", conf.grottport, "\n")
        except:  
            print("IP and port information not available") 

        self.server.listen(0)
        self.forward_to = (conf.growattip, conf.growattport)
        
    def main(self,conf):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept(conf)
                    break
                try: 
                    self.data, self.addr = self.s.recvfrom(buffer_size)
                except: 
                    if conf.verbose : print("\t - Grott connection error")    
                if len(self.data) == 0:
                    self.on_close(conf)
                    break
                else:
                    self.on_recv(conf)

    def on_accept(self,conf):
        forward = Forward().start(self.forward_to[0], self.forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            if conf.verbose: print("\t -", clientaddr, "has connected")
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            if conf.verbose: 
                print("\t - Can't establish connection with remote server."),
                print("\t - Closing connection with client side", clientaddr)
            clientsock.close()

    def on_close(self,conf):
        if conf.verbose: 
            #try / except to resolve errno 107: Transport endpoint is not connected 
            try: 
                print("\t -", self.s.getpeername(), "has disconnected")
            except:  
                print("\t -", "peer has disconnected")

        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self,conf):
        data = self.data      
        print("\t Conections - " + str(len(self.channel)))
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        print("\t - " + "Growatt packet received:   " + today) 
        print("\t\t ", self.channel[self.s])
        print(data)
        bdata = decrypt(data) 
        try:
            serial = codecs.decode(bdata[:48], "hex").decode('utf-8','ignore')
            serial = serial[-16:]
            print('\tSerial Datalogger: '+colored(serial, 'green')) 
        except:
            print(colored(bdata[:48], 'red')) 
#0041000602410103
#004a000602410104
        print('\tHearder Datalogger: '+colored(bdata, 'yellow')) 
        # print('\tHearder : '+colored(bdata[0:16], 'yellow')) 
        # print(colored('0000000000000000'+bdata[16:48], 'yellow')) 
        # print(colored('0000000000000000000000000000000000000000000000000000000000000000'+bdata[64:], 'yellow')) 
        # FILTER!!!!!!!! Detect if configure data is sent!
        header = "".join("{:02x}".format(n) for n in data[0:8])
        print(colored("\t Header               : "+header, 'blue')) 

        if conf.blockcmd : 
            #standard everything is blocked!
            blockflag = True 
            #partly block configure Shine commands    
            h_comd1 = header[14:16]  
            h_comd2 = header[6:8]    
            h_comd3 = header[12:16]
         
            if h_comd1  == "18" :         
                if conf.blockcmd : 
                    if h_comd2 == "05" or h_comd2 == "06" : confdata = decrypt(data) 
                    else :  confdata = data

                    #get conf command (location depends on record type), maybe later more flexibility is needed
                    if h_comd2 == "06" : confcmd = confdata[76:80]
                    else: confcmd = confdata[36:40]
                    
                    if h_comd1 == "18" : 
                        #do not block if configure time command of configure IP (if noipf flag set)
                        if conf.verbose : print("\t - Grott: Shine Configure command detected")                                                    
                        if confcmd == "001f" or (confcmd == "0011" and conf.noipf) : 
                            blockflag = False
                            if confcmd == "001f": confcmd = "Time"
                            if confcmd == "0011": confcmd = "Change IP"
                            if conf.verbose : print("\t - Grott: Configure command not blocked : ->>>>>>>>>>>>>>>>>>", confcmd)    
                    else : 
                        #All configure inverter commands will be blocked
                        if conf.verbose : print("\t - Grott: Inverter Configure command detected")
            
            #allow records: 
            if h_comd3 in conf.recwl : blockflag = False     

            if blockflag : 
                print(colored("\t - Grott: Record blocked: "+ h_comd3))
                return

        h_comd1 = header[12:16]
        if h_comd1  == "0118" : 
            print(colored("\t - comando de restart "+ h_comd1,'red'))        
        # send data to destination
        destination = self.channel[self.s]


        try:
            for dest in self.channel:
                hostname = dest.getpeername()
                print(hostname[0],hostname[1])
                if(hostname[0]=='10.100.33.56'):
                    print('send to', hostname[0],hostname[1])
                    dest.send(data)
        except:
            hostname = ""

        destination.send(data)
        print(colored( destination,'red'))
        #ignorar comandos que não representam dados
        h_comd = header[12:16]  
        if h_comd  == "0103" or h_comd  == "0150":         
            print(colored("\t - Grott: not decrypt data - blocked: "+ h_comd,'red'))
            return


        if len(data) > conf.minrecl :
            #process received data
            procdata(conf,data)    
        else:     
            if conf.verbose: print("\t - " + 'Data less then minimum record length, data not processed = ' + str(len(data)))
                