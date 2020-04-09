import socket
import time
from packet import Packet
from listener import Listener
from constants import MAX_PCKT_SIZE, POLL_INTERVAL, TIMEOUT
from timer import Timer

class ClientHandler:

    def __init__(self, rudp, client_addr, debug):
        self.rudp = rudp
        self.sock = rudp.sock
        self.send_seq = 1
        self.recv_seq = 1
        self.write_buffer = []
        self.read_buffer = b''
        self.timer = None
        self.client_addr = client_addr
        self.connected = True
        self.closed = False
        self.debug = debug
        self.send_synack()

    def send_synack(self):
        pckt = Packet()
        pckt.syn = 1
        pckt.ack = 1
        self.sock.sendto(pckt.encode(), self.client_addr)

    def send_finack(self):
        self.connected = False
        self.write_buffer = []
        pckt = Packet()
        pckt.fin = 1
        pckt.ack = 1
        self.sock.sendto(pckt.encode(), self.client_addr)

    def read_data(self, pckt, source_addr):
        '''
        Receive data from listener and process
        '''
        if self.debug:
            print(pckt)
        # Handle SYN
        if pckt.syn:
            self.send_synack()
            return
        
        # Handle FIN-ACK
        if pckt.fin and pckt.ack:
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
            self.write_buffer = self.write_buffer[count:]
            self.send_seq = pckt.ackno
        else:
            if pckt.seqno == self.recv_seq:
                self.read_buffer += pckt.payload
                self.recv_seq += 1
            pckt = Packet()
            pckt.ack = 1
            pckt.ackno = self.recv_seq
            self.sock.sendto(pckt.encode(), source_addr)

    def write(self, pckt):
        pckt.seqno = self.send_seq + len(self.write_buffer)
        self.sock.sendto(pckt.encode(), self.client_addr)
        self.write_buffer.append(pckt)
        if self.timer == None or not self.timer.running:
            self.timer = Timer(self.timeout, TIMEOUT)
            self.timer.start()

    def timeout(self):
        if len(self.write_buffer) == 0:
            return
        for pckt in self.write_buffer:
            self.sock.sendto(pckt.encode(), self.client_addr)
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
        print('Received FIN-ACK')
        self.write_buffer = []
        if self.timer != None and self.timer.running:
            self.timer.finish()

    def close(self):
        '''
        Close connection and release client handler
        '''
        self.read_buffer = b''
        self.closed = True
        if self.connected:
            self.connected = False
            # Wait till all data is sent
            while len(self.write_buffer) > 0:
                time.sleep(POLL_INTERVAL)
            pckt = Packet()
            pckt.fin = 1
            self.write(pckt)
            # Wait for fin-ack
            while len(self.write_buffer) > 0:
                time.sleep(POLL_INTERVAL)
        self.rudp.close_connection(self.client_addr)