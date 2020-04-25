import os
from threading import Thread
from utils import Util
import time
import socket

CHUNK = 1024 * 100

def handle_client(sock, addr):
    print("Connected to", addr)
    # receive filename
    u = Util(sock)
    fname = u.recv().decode('ascii')
    file_path = '../public/' + fname
    if os.path.isfile(file_path):
        u.send('OK')
    else:
        u.send('File not found!')
        print('File not found!')
        print('Closed connection...', addr)
        sock.close()
        return
    
    f = open(file_path, 'rb')
    idx = 0
    while True:
        data = f.read(CHUNK)
        if not data:
            print('Finished transfer...', addr)
            sock.close()
            f.close()
            return
        u.send(data)
        idx += 1
        print(idx, end='\r')
    # code shouldn't reach here
    print('Something went wrong...', addr)

def server(addr):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(addr)
    server.listen(1)

    while True:
        sc, addr = server.accept()
        Thread(target=handle_client, args=(sc, addr)).start()

if __name__ == "__main__":
    server(("127.0.0.1", 8000))