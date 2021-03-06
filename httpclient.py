#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib 
from urlparse import urlparse


def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host(self,url):
        url=url.split('://')[1]
        hostname=url.split('/')[0]
        host=hostname.split(':')[0]
        try: 
            # retrieves the port number, if given
            port = int(hostname.split(':')[1])
        except:
            # else port 80 is used
            port = 80
        
        return (host,port)
    def connect(self, host, port):
        try:
            soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.connect((host,port))
           
        except socket.error as e:
            print ("failed to create socket")
            print e
            sys.exit()
        return soc

    def get_code(self, data):
        data=data.split(' ')[1]
        return int(data)

    def get_headers(self,data):
        data=data.split('\r\n\r\n')
        data=data[0]
        return data

    def get_body(self, data):
        data=data.split('\r\n\r\n')[1]
        return data

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def get_hostname_target(self,url):
        target = ""	
        hostname = ""
        #https://docs.python.org/2/library/re.html
        (http,uri)=re.split('://',url)
        try:
            hostname = uri.split('/')[0]
            #http://stackoverflow.com/questions/3627270/python-how-exactly-can-you-take-a-string-split-it-reverse-it-and-join-it-back
            target = '/'.join(uri.split('/')[1:])
        except:
	        hostname = uri
	        target = ""  
        return hostname, target

    def GET(self, url, args=None):
        code = 500
        hostname,target=self.get_hostname_target(url)  

        req = "GET /"+target+" HTTP/1.1\r\n"
        req+="Host: "+hostname+"\r\n\r\n"

        try: 
            host,port=self.get_host(url)
            socket=self.connect(host,port)
            socket.sendall(req)
            
            #buffer from recvall
            data=self.recvall(socket)
            code=self.get_code(data)
            body=self.get_body(data)
            if len(data)==0:
                code=404
            socket.close()
        except:
            code=404
        return HTTPResponse(code,body)

    def POST(self, url, args=None):
        code = 500
        data=""
        body=""
        hostname,target=self.get_hostname_target(url)   
  
        if args!=None:
            data=urllib.urlencode(args)
      
        req ="POST /"+target+" HTTP/1.1\r\n"
        req+="Host: "+hostname+"\r\n"
        req+="Content-Type: application/x-www-form-encoded\r\n"
        req+="Content-Length: "+str(len(data))+"\r\n\r\n"
        req=req+data
      
        try: 
            host,port=self.get_host(url)
            socket=self.connect(host,port)
            socket.sendall(req)

            #buffer from recvall
            data=self.recvall(socket)
            code=self.get_code(data)
            body=self.get_body(data)
            if len(data)==0:
                code=404
            socket.close()
        except:
            code=404
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
