import socket
import time
from .packet import Packet
from .listener import Listener
from .constants import MAX_PCKT_SIZE, POLL_INTERVAL, TIMEOUT
from .timer import Timer
import datetime
from threading import Lock

class RUDPClient:
    
    def __init__(self, debug=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # seq no of the first packet in the write buffer
        self.send_seq = 0
        # seq no of the next packet to be received
        self.recv_seq = 0
        self.write_buffer = []
        # mutex locks for write and read buffers
        self.mutex = Lock()
        self.mutexr = Lock()
        self.read_buffer = b''
        self.connected = False
        self.closed = False
        self.timer = None
        # flag to print debug logs
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
            # remove SYN packet from buffer
            self.write_buffer = self.write_buffer[1:]
            self.connected = True
            # update seq numbers
            self.recv_seq += 1
            self.send_seq += 1

    def send_finack(self):
        self.connected = False
        # clear write buffer
        self.write_buffer = []
        pckt = Packet()
        pckt.fin = 1
        pckt.ack = 1
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)
        # send FIN-ACK
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
            # count number of packets which are acked
            count = pckt.ackno - self.send_seq
            if count <= 0:
                return
            # Access write buffer with mutex 
            self.mutex.acquire()
            # remove acked packets from buffer
            self.write_buffer = self.write_buffer[count:]
            self.send_seq = pckt.ackno
            self.mutex.release()
        else:
            # if received expected packet update recv_seq no
            if pckt.seqno == self.recv_seq:
                self.mutexr.acquire()
                self.read_buffer += pckt.payload
                self.recv_seq += 1
                self.mutexr.release()
            pckt = Packet()
            pckt.ack = 1
            pckt.ackno = self.recv_seq
            # send ack 
            self.sock.sendto(pckt.encode(), source_addr)

    def write(self, pckt):
        # Access write buffer with mutex
        self.mutex.acquire()
        # get seqno for the current packet (seq_no of buffer start + len of buffer)
        pckt.seqno = self.send_seq + len(self.write_buffer)
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)
        # append to write buffer for retransmission (if required)
        self.write_buffer.append(pckt)
        self.mutex.release()
        self.sock.sendto(pckt.encode(), self.server_addr)
        # start timer if not running
        if self.timer == None or not self.timer.running:
            self.timer = Timer(self.timeout, TIMEOUT)
            self.timer.start()

    def timeout(self):
        '''
        Callback called on timeout event
        '''
        # no packet to send
        if len(self.write_buffer) == 0:
            return
        # retransmit all packets in write buffer
        for pckt in self.write_buffer:
            if self.debug:
                print(datetime.datetime.now().time())
                print("Packet sent:")
                print(pckt)
            self.sock.sendto(pckt.encode(), self.server_addr)
        # restart timer
        self.timer = Timer(self.timeout, TIMEOUT)
        self.timer.start()

    def recv(self, max_bytes):
        if self.closed:
            raise Exception("Socket closed")
        while True:
            # wait till atleast one byte is available in read buffer (maybe use mutex for read buffer)
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
            # break into packet of maximum size MAX_PCKT_SIZE
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
        # clean up
        self.write_buffer = []
        if self.timer != None and self.timer.running:
            self.timer.finish()
        self.listener.finish()

    def close(self):
        '''
        Close connection (Client initiates closing connection)
        '''
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
            # Wait for fin-ack atmost 100 * POLL_INTERVAL
            cnt = 0
            while len(self.write_buffer) > 0 and cnt < 100:
                time.sleep(POLL_INTERVAL)
                cnt += 1
        self.finack()
        # wait for listener to finish
        time.sleep(2*POLL_INTERVAL)


