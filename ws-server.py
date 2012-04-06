#!/usr/bin/env python

import socket, threading, re
import hashlib, base64
import sys, getopt

# The client sends a Sec-WebSocket-Key which is base64 encoded. To form a response, the magic string
# "258EAFA5-E914-47DA-95CA-C5AB0DC85B11" is appended to this (undecoded) key, and the resulting string is then
# hashed with SHA-1 and then base64 encoded. The result is then replied in the header "Sec-WebSocket-Accept".

magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def handle_ws_request(soc):
    global magic_string
    request = soc.recv(1024)            # a buffer to hold the request
#   print request

    match = re.search("(?<=Sec-WebSocket-Key: ).+", request)
    key = match.group(0).strip()        # nasty "\r\n" at the end
    sha1 = hashlib.sha1()
    sha1.update(key + magic_string)
    h = base64.b64encode(sha1.digest())

    reply = "HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Accept: %s\r\n\r\n" % h
#   print reply

    soc.send(reply)
    while 1:
        stuff = soc.recv(4096)          # a larger buffer to hold whatever stuff coming
        soc.send(stuff)                 # echo back
#   soc.close()



http_port = 8000                        # default to 8000, the same as "python -m SimpleHTTPServer"
websocket_port = 8005

opts, args = getopt.getopt(sys.argv[1:], "o:l:")
for o, v in opts:
    if o == "-o":                       # ws origin
        http_port = int(v)
    elif o == "-l":                     # ws location
        websocket_port = int(v)

soc = socket.socket()
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
soc.bind(('127.1', websocket_port))
soc.listen(5)
while 1:
    t,_ = soc.accept()
    threading.Thread(target = handle_ws_request, args = (t,)).start()
