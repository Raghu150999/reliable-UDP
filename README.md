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