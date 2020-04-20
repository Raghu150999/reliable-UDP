from rudp_server import RUDPServer 
import time

server = RUDPServer(debug=True)
server.bind(("127.0.0.1", 8000))
server.listen()

client, addr = server.accept()
print('Client connected...', addr)

for i in range(1000):
    data = client.recv(2)
    print(i, 'Client message:', data.decode('ascii'), end='\r')
    client.send(data)
print()
client.close()
server.close()