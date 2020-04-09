from rudp_server import RUDPServer 
import time

server = RUDPServer()
server.bind(("127.0.0.1", 8000))
server.listen()

client, addr = server.accept()
print('Client connected...', addr)

data = client.recv(1000)
print('Client message:', data.decode('ascii'))
client.send(data)
client.close()
server.close()