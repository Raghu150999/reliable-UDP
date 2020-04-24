import socket
import time
from .packet import Packet
from .listener import Listener
from .constants import MAX_PCKT_SIZE, POLL_INTERVAL, TIMEOUT, RWND, MAX_BYTES
from .timer import Timer
import datetime
from threading import Lock

class ClientHandler:

    def __init__(self, rudp, client_addr, debug):
        self.rudp = rudp
        self.sock = rudp.sock
        self.send_seq = 1
        self.recv_seq = 1
        self.write_buffer = []
        self.read_buffer = b''
        self.timer = None
        self.order = [None] * MAX_BYTES
        # mutex locks for write and read buffers
        self.mutex = Lock()
        self.mutexr = Lock()
        self.client_addr = client_addr
        self.connected = True
        self.closed = False
        self.debug = debug
        # size of outbound packets
        self.buff = 0
        self.send_synack()

    def send_synack(self):
        pckt = Packet()
        pckt.syn = 1
        pckt.ack = 1
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)
        self.sock.sendto(pckt.encode(), self.client_addr)

    def send_finack(self):
        self.write_buffer = []
        self.connected = False
        pckt = Packet()
        pckt.fin = 1
        pckt.ack = 1
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)
        self.sock.sendto(pckt.encode(), self.client_addr)

    def read_data(self, pckt, source_addr):
        '''
        Receive data from listener and process
        '''
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet received:")
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
            if count <= 0:
                return
            sent = self.write_buffer[:count]
            for p in sent:
                self.buff -= len(p.payload)
            # Access write buffer with mutex 
            self.mutex.acquire()
            self.write_buffer = self.write_buffer[count:]
            self.send_seq = pckt.ackno
            self.mutex.release()
        else:
            idx = pckt.seqno % MAX_BYTES
            if self.order[idx] == None:
                self.order[idx] = pckt
            # if received expected packet update recv_seq no
            if pckt.seqno == self.recv_seq:
                start = idx
                data = b''
                while True:
                    if self.order[start] == None:
                        break
                    data += self.order[start].payload
                    self.order[start] = None
                    start += 1
                    if start > MAX_BYTES:
                        start -= MAX_BYTES
                self.mutexr.acquire()
                self.read_buffer += data
                self.mutexr.release()
                self.recv_seq = start
            pckt = Packet()
            pckt.ack = 1
            pckt.ackno = self.recv_seq
            # send ack 
            self.sock.sendto(pckt.encode(), source_addr)

    def write(self, pckt):
        self.mutex.acquire()
        pckt.seqno = self.send_seq + len(self.write_buffer)
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)
        self.write_buffer.append(pckt)
        self.mutex.release()
        self.sock.sendto(pckt.encode(), self.client_addr)
        if self.timer == None or not self.timer.running:
            self.timer = Timer(self.timeout, TIMEOUT)
            self.timer.start()

    def timeout(self):
        if len(self.write_buffer) == 0:
            return
        cnt = 0
        for pckt in self.write_buffer:
            cnt += 1
            if self.debug:
                print(datetime.datetime.now().time())
                print("Packet sent:")
                print(pckt)
            self.sock.sendto(pckt.encode(), self.client_addr)
            if cnt >= RWND:
                break
        self.timer = Timer(self.timeout, TIMEOUT)
        self.timer.start()

    def recv(self, max_bytes):
        if self.closed:
            raise Exception("Socket closed")
        while True:
            if len(self.read_buffer) > 0:
                self.mutexr.acquire()
                l = min(len(self.read_buffer), max_bytes)
                data = self.read_buffer[:l]
                self.read_buffer = self.read_buffer[l:]
                self.mutexr.release()
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
            # wait till receiver has acked enough bytes
            while self.buff + rem > MAX_BYTES:
                time.sleep(POLL_INTERVAL)
            self.buff += rem
            data = data[rem:]
            pckt = Packet()
            pckt.payload = payload
            self.write(pckt)

    def finack(self):
        self.write_buffer = []
        if self.timer != None and self.timer.running:
            self.timer.finish()

    def close(self):
        '''
        Close connection and release client handler
        '''
        self.closed = True
        if self.connected:
            self.connected = False
            # Wait till all data is sent
            while len(self.write_buffer) > 0:
                time.sleep(POLL_INTERVAL)
            pckt = Packet()
            pckt.fin = 1
            self.write(pckt)
            # Wait for fin-ack atmost 100 * POLL_INTERVAL
            cnt = 0
            while len(self.write_buffer) > 0 and cnt < 100:
                time.sleep(POLL_INTERVAL)
                cnt += 1
        self.finack()
        self.rudp.close_connection(self.client_addr)