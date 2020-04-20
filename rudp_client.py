import socket
import time
from packet import Packet
from listener import Listener
from constants import MAX_PCKT_SIZE, POLL_INTERVAL, TIMEOUT
from timer import Timer
import datetime
from threading import Lock

class RUDPClient:
    
    def __init__(self, debug=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_seq = 0
        self.recv_seq = 0
        self.write_buffer = []
        self.mutex = Lock()
        self.read_buffer = b''
        self.connected = False
        self.closed = False
        self.timer = None
        self.debug = debug

    def connect(self, address):
        # Create a SYN packet
        pckt = Packet()
        pckt.syn = 1
        self.listener = Listener(self)
        self.listener.start()
        self.server_addr = address
        self.write(pckt)
        # Wait till connection is established
        while not self.connected:
            time.sleep(POLL_INTERVAL)

    def synack(self):
        '''
        Called when client receives SYN-ACK from server
        '''
        if not self.connected:
            self.connected = True
            self.recv_seq += 1
            self.send_seq += 1
            self.write_buffer = self.write_buffer[1:]

    def send_finack(self):
        self.connected = False
        self.write_buffer = []
        pckt = Packet()
        pckt.fin = 1
        pckt.ack = 1
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)
        self.sock.sendto(pckt.encode(), self.server_addr)

    def read_data(self, pckt, source_addr):
        '''
        Receive data from listener process
        Note: this function is upcalled by the listener thread
        '''
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet received:")
            print(pckt)
        
        # Ignore unknown response
        if source_addr != self.server_addr:
            return
        
        # Handle SYN-ACK
        if pckt.ack and pckt.syn:
            self.synack()
            return
        
        # Handle FIN-ACK
        if pckt.ack and pckt.fin:
            self.finack()
            return

        # Handle FIN
        if pckt.fin:
            self.send_finack()
            return
        
        # If ACK packet (no piggy backed ack for now)
        # Discarding out of order packets for now
        if pckt.ack:
            count = pckt.ackno - self.send_seq
            if count <= 0:
                return
            # Access write buffer with mutex 
            self.mutex.acquire()
            self.write_buffer = self.write_buffer[count:]
            self.send_seq = pckt.ackno
            self.mutex.release()
        else:
            if pckt.seqno == self.recv_seq:
                self.read_buffer += pckt.payload
                self.recv_seq += 1
            pckt = Packet()
            pckt.ack = 1
            pckt.ackno = self.recv_seq
            self.sock.sendto(pckt.encode(), source_addr)

    def write(self, pckt):
        # Access write buffer with mutex
        self.mutex.acquire()
        pckt.seqno = self.send_seq + len(self.write_buffer)
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)
        self.write_buffer.append(pckt)
        self.mutex.release()
        self.sock.sendto(pckt.encode(), self.server_addr)
        if self.timer == None or not self.timer.running:
            self.timer = Timer(self.timeout, TIMEOUT)
            self.timer.start()

    def timeout(self):
        if len(self.write_buffer) == 0:
            return
        for pckt in self.write_buffer:
            if self.debug:
                print(datetime.datetime.now().time())
                print("Packet sent:")
                print(pckt)
            self.sock.sendto(pckt.encode(), self.server_addr)
        self.timer = Timer(self.timeout, TIMEOUT)
        self.timer.start()

    def recv(self, max_bytes):
        if self.closed:
            raise Exception("Socket closed")
        while True:
            if len(self.read_buffer) > 0:
                l = min(len(self.read_buffer), max_bytes)
                data = self.read_buffer[:l]
                self.read_buffer = self.read_buffer[l:]
                return data
            if not self.connected:
                return None
            time.sleep(POLL_INTERVAL)

    def send(self, data):
        '''
        Packetize the data and write
        '''
        if self.closed:
            raise Exception("Socket closed")
        if not self.connected:
            raise Exception("Peer disconnected")
        while len(data) > 0:
            rem = min(len(data), MAX_PCKT_SIZE)
            payload = data[:rem]
            data = data[rem:]
            pckt = Packet()
            pckt.payload = payload
            self.write(pckt)

    def finack(self):
        '''
        Assumption is that the server will stay active to send fin-ack even after 
        it has received fin twice
        '''
        self.write_buffer = []
        if self.timer != None and self.timer.running:
            self.timer.finish()
        self.listener.finish()

    def close(self):
        '''
        Close connection (Client initiates closing connection)
        '''
        # TODO: handle case when server disconnects without acking the FIN
        self.read_buffer = b''
        self.closed = True
        if self.connected:
            self.connected = False
            # Wait till all data is sent
            while len(self.write_buffer) > 0:
                time.sleep(POLL_INTERVAL)
            # send FIN
            pckt = Packet()
            pckt.fin = 1
            self.write(pckt)
            # Wait for FIN-ACK
            while len(self.write_buffer) > 0:
                time.sleep(POLL_INTERVAL)
        if self.timer != None and self.timer.running:
            self.timer.finish()
        self.listener.finish()
        time.sleep(2*POLL_INTERVAL)


