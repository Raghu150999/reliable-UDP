from rudp.rudp_server import RUDPServer
from threading import Thread, Lock
from utils import Util


class Server:
    '''
    Chat server for multiple clients, client join the chat room
    send and receive messages to/from all participants
    '''
    def __init__(self, addr):
        '''
        Args:
            addr: server address (IP, port)
        '''
        self.sock = RUDPServer()
        self.sock.bind(addr)
        self.sock.listen()
        print('Chat server started at', addr)
        self.clients = {}
        self.mutex = Lock()
        # number of participants
        self.nop = 0
        # accept connections forever
        while True:
            sc, addr = self.sock.accept()
            self.clients[addr] = Util(sc)
            Thread(target=self.handle_client, args=(sc, addr)).start()
    
    def broadcast(self, msg, sender='SYSTEM', sender_addr=None):
        '''
        Broadcast message to all participants
        Args:
            msg: message to be sent
            sender: name of the sender
        '''
        send_msg = f'{sender}: {msg}'
        self.mutex.acquire()
        # broadcast to everyone
        for caddr in self.clients:
            # don't broadcast to sender
            if caddr == sender_addr:
                continue
            try:
                self.clients[caddr].send(send_msg)
            except Exception as e:
                pass
        self.mutex.release()

    def handle_client(self, sock, addr):
        u = Util(sock)
        # receive username
        username = u.recv().decode('ascii')
        # send number of participants
        self.nop += 1
        u.send(str(self.nop))
        self.broadcast(f'{username} joined')
        while True:
            msg = u.recv().decode('ascii')
            if msg == "!exit":
                self.nop -= 1
                self.mutex.acquire()
                sock.close()
                del self.clients[addr]
                self.mutex.release()
                self.broadcast(f'{username} left')
                return
            self.broadcast(msg, sender=username, sender_addr=addr)

if __name__ == "__main__":
    server = Server(("127.0.0.1", 8000))
