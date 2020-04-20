from rudp.rudp_client import RUDPClient
from threading import Thread
from utils import Util
import argparse

class Client:
    '''
    Client class for setting up connection to chat server
    '''

    def __init__(self, addr, username):
        '''
        Args:
            addr: server address
            username: username of client
        '''
        self.sock = RUDPClient()
        self.sock.connect(addr)
        u = Util(self.sock)
        self.u = u
        u.send(username)
        msg = u.recv().decode('ascii')
        print('Connection established...')
        print('Number of participants:', msg)
    
    def send(self, msg):
        '''
        Send message to chat server
        '''
        self.u.send(msg)

    def recv(self):
        '''
        Returns:
            message in chat
        '''
        return self.u.recv().decode('ascii')
    
    def close(self):
        self.sock.close()

def read_message(client):
    '''
    Helper function to constantly read messages from client
    '''
    while True:
        msg = input()
        client.send(msg)
        if msg == "!exit":
            client.close()
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser('Chat Server client-end')
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='server IP')
    parser.add_argument('--port', type=int, default=8000, help='server port')
    parser.add_argument('--uname', type=str, help='username', required=True)
    args = parser.parse_args()
    
    print("-" * 60)
    client = Client((args.ip, args.port), args.uname)
    print('Joined chat server...')
    print("Type your message in a single line, hit ENTER to send")
    print("Use '!exit' as message to quit")
    print("-" * 60)
    print()

    # start receiver thread (listen to user input)
    Thread(target=read_message, args=(client,)).start()

    while True:
        try:
            msg = client.recv()
            print(msg)
        except:
            print('Connection closed...')
            break

