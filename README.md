# Reliable-UDP
Reliable transport layer over UDP


## TODO:
- convert write buffer to python queue
- create testing scripts
- raise connection refused error if server is not accepting SYN requests
- use mutex wherever possible, instead of sleep
- implement piggy backed ack
- use byte seqno
- store out of order packets (using byte array)
- implement fast retransmission on 3 dup acks
- use mutex for read buffer
- maintain max buffer size, block send if excedes max buffer size
- build chat application
- implement byte stream instead of write buffer
- handle out of order packet efficiently

## Results:

Comparison of TCP vs RUDP in terms of:
1. Time taken for file transfer (s)
2. Data transmitted (including retransmission) (MB)

We use a MTU of 1500 bytes for network emulation

file size 8.7 MB

delay (ms) | jitter (ms) | loss (%) | TCP time(s) | RUDP time(s) | TCP data(MB) | RUDP data(MB)
-----------|-------------|----------|-------------|--------------|--------------|----------------
   50      |    10       |     5    |    110      |    60        |     9        |      12
   50      |    10       |     20   |    