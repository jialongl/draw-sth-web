#!/usr/bin/env python

import socket, threading, re
import hashlib, base64
import sys, getopt
from util import *

websocket_port = 8005

# The client sends a Sec-WebSocket-Key which is base64 encoded. To form a response, the magic string
# "258EAFA5-E914-47DA-95CA-C5AB0DC85B11" is appended to this (undecoded) key, and the resulting string is then
# hashed with SHA-1 and then base64 encoded. The result is then replied in the header "Sec-WebSocket-Accept".

def reply_ws_request (sock, addr):
    magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    request = sock.recv(1024)                                         # a buffer to hold the request
    log("New connection from " + str(addr))
    log(request)

    match = re.search("(?<=Sec-WebSocket-Key: ).+", request)
    key = match.group(0).strip()                                      # nasty "\r\n" at the end
    sha1 = hashlib.sha1()
    sha1.update(key + magic_string)
    h = base64.b64encode(sha1.digest())

    reply = "HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Accept: %s\r\n\r\n" % h
    log(reply)

    sock.send(reply)
    log("Done handshaking.")


# send whatever stuff drawer_sock received to guesser_sock
def drawer_thread (drawer_sock, guesser_sock):
    b = True
    while b:
        data = drawer_sock.recv(4096)
        try:
            guesser_sock.send(data)
        except:
            b = False
    drawer_sock.close()

def guesser_thread (guesser_sock, answer):
    data = True
    while data:
        data = decode_hybi(guesser_sock.recv(4096))['payload']
        if data == answer:
            msg = encode_hybi("You got it right!", 0x1)
            guesser_sock.send(msg)
            guesser_sock.close()
            data = False

def start_guessing_game (drawer_sock, guesser_sock):
    le_answer = decode_hybi(drawer_sock.recv(64))['payload']
    msg = encode_hybi("set the word liaw.", 0x1)
    guesser_sock.send(msg)

    threading.Thread(target =  drawer_thread, args = (drawer_sock, guesser_sock)).start()
    threading.Thread(target = guesser_thread, args = (guesser_sock, le_answer)).start()



opts, args = getopt.getopt(sys.argv[1:], "l:")
for k, v in opts:
    if k == "-l":                                                     # ws location
        websocket_port = int(v)

listening_sock = socket.socket()
listening_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening_sock.bind(('127.1', websocket_port))
listening_sock.listen(2)

queue_addrs = []
queue_socks = []

while True:
    conn_sock, addr = listening_sock.accept()
    reply_ws_request(conn_sock, addr)

    queue_socks.append(conn_sock)
    queue_addrs.append(addr)

    if len(queue_addrs) >= 2:
        sock1 = queue_socks.pop(0)
        sock2 = queue_socks.pop(0)
        addr1 = queue_addrs.pop(0)
        addr2 = queue_addrs.pop(0)
        threading.Thread(target = start_guessing_game, args = (sock1, sock2)).start()
