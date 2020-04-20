from rudp_client import RUDPClient

client = RUDPClient(debug=True)
client.connect(("127.0.0.1", 8000))
print('Connected established...')

for i in range(500):
    client.send('hi'.encode('ascii'))
    client.send('hi'.encode('ascii'))
    msg = client.recv(2)
    msg = client.recv(2)
    print(i, 'Server reply:', msg.decode('ascii'), end='\r')
print()
client.close()