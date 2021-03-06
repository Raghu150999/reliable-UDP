# Reliable-UDP
Reliable transport layer over UDP. This project aims to provide reliable transport layer protocol using unreliable UDP protocol. The major motivation to do this is to improve the transmission rates under a lossy network. TCP congestion window significantly cuts down the transmission rate when losses are encountered. However, in this project we propose RUDP which improves the transmission rates significantly using redundant fast retransmissions.

## Usage

### Importing RUDP server and client classes
``` python
from rudp.rudp_server import RUDPServer
from rudp.rudp_client import RUDPClient
```

### Creating a server socket
``` python
server = RUDPServer()
server.bind(addr)
server.listen()
```

### Accept new connection
``` python
sock, addr = server.accept()
```
*`accept()` blocks until new connection request is received by the server*

### Send and Receive
``` python
sock.send(data)
data = sock.recv(1024)
```
*`recv()` returns atmost `1024 bytes` and atleast `1 byte`.*
*If send buffer is full `send()` blocks. Will only return after entire `data` is load into send buffer*

### Creating a client socket
``` python
sock = RUDPClient()
```

### Connecting to server
``` python
sock.connect(server_addr)
```
*Here, server_addr is like `("127.0.0.1", 8000)` i.e. (ip, port) tuple*

### Closing socket
``` python 
sock.close()
```

## Emulating network parameters on localhost
Set MTU (Maximum Transmission Unit):
``` bash
$ sudo ifconfig lo mtu 1500
```

Add network parameters:
``` bash
$ sudo tc qdisc add dev lo root netem delay 50ms 10ms loss 5% corrupt 5% duplicate 1%
```

Remove parameters:
``` bash
$ sudo tc qdisc del dev lo root
```

## TODO:
- convert write buffer to python queue
- implement piggy backed ack
- implement fast retransmission on 3 dup acks

## Results:

Comparison of TCP vs RUDP in terms of:
1. Time taken for file transfer (s)
2. Data transmitted (including retransmission) (MB)

We use a MTU of 1500 bytes for network emulation

actual file size 8.7 MB

*Note: with any loss more than 15% TCP would take hours to finish. However, RUDP still completes within reasonable time*

delay (ms) | jitter (ms) | loss (%) | TCP time(s) | RUDP time(s) | TCP data(MB) | RUDP data(MB)
-----------|-------------|----------|-------------|--------------|--------------|----------------
   50      |    10       |     1    |     42      |    33        |     9        |      11
   50      |    10       |     5    |    110      |    60        |     9        |      12
   50      |    10       |    10    |    234      |   113        |     9        |      15
  100      |    20       |     1    |     68      |    42        |     9        |      11
  100      |    20       |     5    |    236      |    84        |     9        |      14

*Although, RUDP performs better in terms of time for transfer. However, it does more data transfer than TCP*

## Framework:

<img src="plots/rudp-framework.png?raw=true" width="800">

## Applications:

### Minimalist Chat Server
- start chat server: `$ python3 chat_server.py`
- start client session (new terminal): `$ python3 chat_client.py --uname <client's username>`
*Use same command, with different usernames on different terminals for multiple clients*

### File transfer:
- start file server: `$ python3 file_server.py`
- start client file transfer `$ python3 file_client.py --filename test2.mp4`
*Note: server serves all files inside the `public/` directory. `test2.mp4` is a file inside the `public/` directory*

