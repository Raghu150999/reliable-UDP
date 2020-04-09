import socket
import threading, time
from packet import Packet
from constants import MAX_BYTES, POLL_INTERVAL

class Listener(threading.Thread):
    '''
    Listener class to read data from socket and return it to corresponding higher level socket.
    '''
    def __init__(self, rudp_sock):
        threading.Thread.__init__(self)
        self.rudp_sock = rudp_sock
        self.running = True
        
    def run(self):
        # TODO: perfrom upcall on a separate thread
        self.rudp_sock.sock.setblocking(False)
        print('Listener started...')
        while True:
            # Receive datagram
            try:
                msg, source_addr = self.rudp_sock.sock.recvfrom(MAX_BYTES)
                pckt = Packet(msg)
                self.rudp_sock.read_data(pckt, source_addr)
            except socket.error as e:
                time.sleep(POLL_INTERVAL)
            if self.running == False:
                print("Listener finished...")
                exit(0)

    def finish(self):
        self.running = False

    