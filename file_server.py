import os
from rudp.rudp_server import RUDPServer 
from threading import Thread
from utils import Util
import time

CHUNK = 1024 * 100

def handle_client(sock, addr):
    print("Connected to", addr)
    # receive filename
    u = Util(sock)
    fname = u.recv().decode('ascii')
    file_path = 'public/' + fname
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
        print(idx, 'buff size:', sock.buff, end='\r')
    # code shouldn't reach here
    print('Something went wrong...', addr)

def server(addr):
    sock = RUDPServer()
    sock.bind(addr)
    sock.listen()

    while True:
        sc, addr = sock.accept()
        # Thread(target=handle_client, args=(sc, addr)).start()
        handle_client(sc, addr)

if __name__ == "__main__":
    server(("127.0.0.1", 8000))