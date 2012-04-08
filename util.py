import struct, numpy

debug = True

def log (stuff):
    global debug
    if debug:
        print stuff


# The following 2 methods are adapted from: http://www.vncfx.com/noVNC/utils/websocket.py

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

    b1 = 0x80 | (opcode & 0x0f)                                       # FIN + opcode
    payload_len = len(buf)
    if payload_len <= 125:
        header = struct.pack('>BB', b1, payload_len)
    elif payload_len > 125 and payload_len < 65536:
        header = struct.pack('>BBH', b1, 126, payload_len)
    elif payload_len >= 65536:
        header = struct.pack('>BBQ', b1, 127, payload_len)

    log("Encoded: %s" % repr(header + buf))
    return header + buf


def decode_hybi(buf, base64=False):
    """ Decode HyBi style WebSocket packets.
    Returns:
        {'fin'          : 0_or_1,
         'opcode'       : number,
         'mask'         : 32_bit_number,
         'hlen'         : header_bytes_number,
         'length'       : payload_bytes_number,
         'payload'      : decoded_buffer,
         'left'         : bytes_left_number,
         'close_code'   : number,
         'close_reason' : string}
    """

    f = {'fin'          : 0,
         'opcode'       : 0,
         'mask'         : 0,
         'hlen'         : 2,
         'length'       : 0,
         'payload'      : None,
         'left'         : 0,
         'close_code'   : None,
         'close_reason' : None}

    blen = len(buf)
    f['left'] = blen

    if blen < f['hlen']:
        return f                                                      # Incomplete frame header

    b1, b2 = struct.unpack_from(">BB", buf)
    f['opcode'] = b1 & 0x0f
    f['fin'] = (b1 & 0x80) >> 7
    has_mask = (b2 & 0x80) >> 7

    f['length'] = b2 & 0x7f

    if f['length'] == 126:
        f['hlen'] = 4
        if blen < f['hlen']:
            return f                                                  # Incomplete frame header
        (f['length'],) = struct.unpack_from('>xxH', buf)
    elif f['length'] == 127:
        f['hlen'] = 10
        if blen < f['hlen']:
            return f                                                  # Incomplete frame header
        (f['length'],) = struct.unpack_from('>xxQ', buf)

    full_len = f['hlen'] + has_mask * 4 + f['length']

    if blen < full_len:                                               # Incomplete frame
        return f                                                      # Incomplete frame header

    # Number of bytes that are part of the next frame(s)
    f['left'] = blen - full_len

    # Process 1 frame
    if has_mask:
        # unmask payload
        f['mask'] = buf[f['hlen']:f['hlen']+4]
        b = c = ''
        if f['length'] >= 4:
            mask = numpy.frombuffer(buf, dtype=numpy.dtype('<u4'),
                    offset=f['hlen'], count=1)
            data = numpy.frombuffer(buf, dtype=numpy.dtype('<u4'),
                    offset=f['hlen'] + 4, count=int(f['length'] / 4))
            #b = numpy.bitwise_xor(data, mask).data
            b = numpy.bitwise_xor(data, mask).tostring()

        if f['length'] % 4:
            #print("Partial unmask")
            mask = numpy.frombuffer(buf, dtype=numpy.dtype('B'),
                    offset=f['hlen'], count=(f['length'] % 4))
            data = numpy.frombuffer(buf, dtype=numpy.dtype('B'),
                    offset=full_len - (f['length'] % 4),
                    count=(f['length'] % 4))
            c = numpy.bitwise_xor(data, mask).tostring()
        f['payload'] = b + c
    else:
        print("Unmasked frame: %s" % repr(buf))
        f['payload'] = buf[(f['hlen'] + has_mask * 4):full_len]

    if base64 and f['opcode'] in [1, 2]:
        try:
            f['payload'] = b64decode(f['payload'])
        except:
            print("Exception while b64decoding buffer: %s" %
                    repr(buf))
            raise

    if f['opcode'] == 0x08:
        if f['length'] >= 2:
            f['close_code'] = struct.unpack_from(">H", f['payload'])
        if f['length'] > 3:
            f['close_reason'] = f['payload'][2:]

    return f
