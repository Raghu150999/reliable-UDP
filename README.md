# Reliable-UDP
Reliable transport layer over UDP


## TODO:
1. convert write buffer to python queue
2. do proper close handling
3. create testing scripts
4. handling if no response sent from peer (timeout)
5. raise connection refused error if server is accepting SYN requests
6. use mutex wherever possible, instead of time.sleep
7. implement piggy backed ack
8. use byte seqno
9. store out of order packets (using byte array)
10. implement fast retransmission on 3 dup acks
11. use mutex for read buffer