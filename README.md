# Reliable-UDP
Reliable transport layer over UDP


## TODO:
- convert write buffer to python queue
- raise connection refused error if server is not accepting SYN requests
- use mutex wherever possible, instead of sleep
- implement piggy backed ack
- implement fast retransmission on 3 dup acks
- maintain max buffer size, block send if exceedes max buffer size

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

