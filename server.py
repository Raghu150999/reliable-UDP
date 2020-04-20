from rudp_server import RUDPServer 
import time
import struct

def echo_server(addr):
    '''
    Simple echo server
    '''
    server = RUDPServer()
    server.bind(addr)
    server.listen()

    client, addr = server.accept()
    print('Client connected...', addr)

    while True:
        data = client.recv(2)
        if not data:
            break
        print('Client message:', data.decode('ascii'), end='\r')
        client.send(data)
    client.close()
    server.close()

def addition_server(addr):
    '''
    Adds 2 numbers and returns the sum
    '''
    server = RUDPServer()
    server.bind(addr)
    server.listen()

    client, addr = server.accept()
    print('Client connected...', addr)

    while True:
        # receive 4 byte number
        n1 = client.recv(4)
        if not n1:
            break
        n1, = struct.unpack('!I', n1)

        n2 = client.recv(4)
        n2, = struct.unpack('!I', n2)

        s = n1 + n2
        s = struct.pack('!I', s)
        client.send(s)
    client.close()
    server.close()

if __name__ == "__main__":
    # addition_server(("127.0.0.1", 8000))
    echo_server(("127.0.0.1", 8000))