import socket
import struct
from uuid import uuid4
from threading import Thread

multicast_addr = '224.0.0.0'
bind_addr = '0.0.0.0' # Bind to all interfaces in the system
port = 3000

class MulticastPeer(Thread):
    def __init__(self):
        Thread.__init__(self)

        #### Network 
        # Socket para IPv4, UDP(Datagramas)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Configuração para socket multicast (não tem uma classe especifica como em Java)
        membership = socket.inet_aton(multicast_addr) + socket.inet_aton(bind_addr)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((bind_addr, port))

        #### Thread
        # Inicia thread de leitura de mensagens
        self.start()

        #### Peer object
        # Obtem um uuid aleatorio
        self.UUID = uuid4()


    def getInput(self):
        while True:
            msg = input("Digite a mensagem: ")
            # Envia msg para grupo multicast
            msg = str(self.UUID) + msg
            self.sock.sendto(msg.encode('UTF-8'), (multicast_addr, port))

    def run(self):
        while True:
            msg, addr = self.sock.recvfrom(255)
            print(msg.decode('UTF-8'), addr)