from rudp.rudp_client import RUDPClient
import struct

def echo_client(addr):
    client = RUDPClient()
    client.connect(addr)
    print('Connection established...')

    for i in range(100):
        client.send('hi'.encode('ascii'))
        msg = client.recv(2).decode('ascii')
        assert(msg == 'hi')
        print(i, 'Server reply:', msg, end='\r')
    print()
    client.close()

def addition_client(addr):
    client = RUDPClient()
    client.connect(addr)
    print("Connection established...")

    for i in range(100):
        n = 2 * i + 15
        a = n
        n = struct.pack('!I', n)
        client.send(n)
        n = 3 * i + 10
        b = n
        n = struct.pack('!I', n)
        client.send(n)
        s = client.recv(4)
        s, = struct.unpack('!I', s)
        assert(s == a + b)
        print('Numbers are:', a, b, s, end='\r')
    client.close()

def echo2_client(addr):
    client = RUDPClient()
    client.connect(addr)
    print('Connection established...')

    # rapid send
    for i in range(100):
        client.send('hi'.encode('ascii'))
    print('send complete!')

    # recv all replies
    for i in range(100):
        msg = client.recv(2).decode('ascii')
        assert(msg == 'hi')
        print(i, 'Server reply:', msg, end='\r')
    print()
    client.close()

if __name__ == "__main__":
    # addition_client(("127.0.0.1", 8000))
    echo2_client(("127.0.0.1", 8000))