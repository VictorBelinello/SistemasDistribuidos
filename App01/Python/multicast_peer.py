import socket
import struct
from threading import Thread

multicast_addr = '224.0.0.0'
bind_addr = '0.0.0.0' # Bind to all interfaces in the system
port = 3000

class MulticastPeer(Thread):
    def __init__(self, msg):
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        membership = socket.inet_aton(multicast_addr) + socket.inet_aton(bind_addr)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((bind_addr, port))

        self.sock.sendto(msg.encode(), (multicast_addr, port))
        self.start()

    def run(self):
        while True:
            msg, addr = self.sock.recvfrom(255)
            print(msg, addr)