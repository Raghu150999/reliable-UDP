import socket
import time
import struct
from threading import Thread

def handle_client(sock, addr):
    while True:
        data = sock.recv(2)
        if not data:
            break
        print('Client message:', data.decode('ascii'), end='\r')
        sock.send(data)
    print('Client finished...', addr)
    sock.close()

def echo_server(addr):
    '''
    Simple echo server, handling multiple clients with multi-threading
    '''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(addr)
    server.listen(1)
    while True:
        client, addr = server.accept()
        print('Client connected...', addr)
        Thread(target=handle_client, args=(client, addr)).start()

def addition_server(addr):
    '''
    Adds 2 numbers and returns the sum
    '''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(addr)
    server.listen(1)

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