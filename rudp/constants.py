MAX_BYTES = 90000 # 65535 should be less than receiver buffer size
MAX_PCKT_SIZE = 1460
POLL_INTERVAL = 0.1 # 10 polls / sec
HEADER_SIZE = 9
TIMEOUT = 0.2 # seconds
RWND = 10 # Retransmission window size (maximum no of packets to be retransmitted after timeout)

'''
We can increase the RWND, and decrease TIMEOUT for more retransmissions. This decreases the overall time taken for file transfer. However, it increases the net data transmitted i.e. more data transfer happens due to excessive retransmission
'''