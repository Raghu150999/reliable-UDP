from rudp.rudp_client import RUDPClient
from utils import Util
import time

def client(addr, filename):
    sock = RUDPClient()
    sock.connect(addr)
    print('Connection established...')
    u = Util(sock)
    u.send(filename)
    status = u.recv().decode('ascii')
    if status != "OK":
        print(status)
        sock.close()
        return
    f = open(filename, 'wb')
    print('Started file transfer...')
    start_time = time.time()
    idx = 0
    while True:
        data = u.recv()
        idx += 1
        print('Block:', idx, end='\r')
        if not data:
            print('Finished file transfer...')
            end_time = time.time()
            diff = end_time - start_time
            print('time taken: ', diff, 's')
            break
        f.write(data)
    f.close()
    sock.close()


if __name__ == "__main__":
    client(("127.0.0.1", 8000), 'test.mp4')
