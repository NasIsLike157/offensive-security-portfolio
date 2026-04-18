import struct


class ICMP():
    def __init__(self,buf):
        header = struct.unpack('<BBHHH', buf)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]