import struct
import socket

class Util:
    '''
    Helper functions for socket operations
    '''

    def __init__(self, sock):
        self.sock = sock

    def recvall(self, length):
        data = b''
        rem = length
        while rem > 0:
            new_data = self.sock.recv(rem)
            if not new_data:
                raise Exception('peer closed')
            data += new_data
            rem = length - len(data)
        return data
    
    def recv(self):
        l = self.sock.recv(4)
        if not l:
            return None
        assert(len(l) == 4)
        l, = struct.unpack('!I', l)
        data = self.recvall(l)
        return data
    
    def send(self, data):
        if type(data) == str:
            data = data.encode('ascii')
        l = len(data)
        l = struct.pack('!I', l)
        databytes = l
        databytes += data
        self.sock.send(databytes)