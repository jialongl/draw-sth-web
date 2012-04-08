#!/usr/bin/env python

import socket, threading, re
import hashlib, base64
import sys, getopt
import struct

debug = True
websocket_port = 8005

def log (stuff):
    global debug
    if debug:
        print stuff

def encode_hybi(buf, opcode, base64=False):
    """ Encode a HyBi style websocket frame.
    Opcode:
        0x0 - continuation
        0x1 - text frame (base64 encode buf)
        0x2 - binary frame (use raw buf)
        0x8 - connection close
        0x9 - ping
        0xA - pong
    """
    if base64:
        buf = b64encode(buf)

    b1 = 0x80 | (opcode & 0x0f) # FIN + opcode
    payload_len = len(buf)
    if payload_len <= 125:
        header = struct.pack('>BB', b1, payload_len)
    elif payload_len > 125 and payload_len < 65536:
        header = struct.pack('>BBH', b1, 126, payload_len)
    elif payload_len >= 65536:
        header = struct.pack('>BBQ', b1, 127, payload_len)

    log("Encoded: %s" % repr(header + buf))
    return header + buf, len(header), 0

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


def start_guessing_game (drawer_sock, guesser_sock):
    le_answer = drawer_sock.recv(64)
    msg,_,_ = encode_hybi("set the word liaw.", 0x1)
    guesser_sock.send(msg)

    # send whatever stuff drawer_sock received to guesser_sock
    data = True
    while data:
        data = drawer_sock.recv(4096)
        guesser_sock.send(data)


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
