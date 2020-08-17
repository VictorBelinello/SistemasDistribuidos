from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

import socket
import struct
from threading import Thread, active_count
from uuid import uuid4

### Constantes relativas à conexao 
MULTICAST_ADDR = '224.0.0.0'
BIND_ADDR = '0.0.0.0' # Bind to all interfaces in the system
PORT = 3000

#### Constantes relativas ao header da mensagem
# Header:   UUID | Porta unicast | Tipo mensagem | Tamanho mensagem | 
# UUID
UUID_BYTES = 32 + 4 # UUID tem 128bits = 32bytes. Alem disso tem 4bytes para separadores
UUID_RANGE = slice(0,UUID_BYTES) # Logo na mensagem o UUID esta na faixa [0:36]

# Porta unicast
PORT_RANGE = slice(UUID_RANGE.stop, UUID_RANGE.stop + 5) # 5 caracteres logo apos UUID

# Tipo mensagem
MSG_TYPE_RANGE = slice(PORT_RANGE.stop , PORT_RANGE.stop + 1) # Tipo da mensagem tem 1 char apenas 
MSG_TYPE_PUBKEY = "0"
MSG_TYPE_NORMAL = "2"


# Tamanho mensagem
import math
MSG_MAX_CHAR = 10000 # Numero maximo de caracteres da mensagem
MAX_NUMBER_DIGITS_MSG = int(math.log10(MSG_MAX_CHAR)) + 1  # Numero de char/digitos necessarios para representar o tamanho da mensagem. Exemplo: Se a mensagem tiver 2487 caracteres, para representar tal tamanho precisamos de 4 caracteres ('2','4','8','7')
MSG_SIZE_RANGE = slice(MSG_TYPE_RANGE.stop, MSG_TYPE_RANGE.stop + MAX_NUMBER_DIGITS_MSG) 

# Inicio da mensagem em si
MSG_START_BYTE = MSG_SIZE_RANGE.stop

# Create multicast and unicast sockets
def createSockets():
    # Multicast socket
    # Datagram socket for IPv4
    multi_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Allow for address reuse (same machine same addr)
    multi_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # To join multicast group change the option IP_ADD_MEMBERSHIP, a 8-byte representation of:
    # multicast group address + network interface to listen
    membership = struct.pack("=4sL", socket.inet_aton(MULTICAST_ADDR), socket.INADDR_ANY)
    multi_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    # Bind socket to all interfaces
    addr = (BIND_ADDR, PORT)
    multi_socket.bind(addr)


    # Unicast socket
    uni_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # If port = 0 a random available port is assigned
    addr = ('', 0)
    uni_socket.bind(addr)

    return uni_socket, multi_socket

# Add header
def addHeader(uuid, port, msgType, msg):
    # Make a fixed lenght string containing the size of msg
    msgSize = str(len(msg))
    msgSize = msgSize.zfill(MAX_NUMBER_DIGITS_MSG)

    # Make a fixedd lenght string containing the unicast port
    portSize = len(str(port))
    port = str(port).zfill(5) # Around 64k ports ~ 5 digits

    # Make header
    header = uuid + port + msgType + msgSize

    # Add header to msg and return in bytes format
    return (header + msg).encode("UTF-8")

# Parse data received in bytes
def parseBytesData(data):
    # The constants *_RANGE are of type slice [START:END]
    uuid = data[UUID_RANGE].decode("UTF-8")
    
    unicast_port = int( data[PORT_RANGE].decode("UTF-8") )
    
    msg_type = data[MSG_TYPE_RANGE].decode("UTF-8")
    
    msg_size = int(data[MSG_SIZE_RANGE])

    msg_end_byte = MSG_START_BYTE + msg_size
    msg = data[MSG_START_BYTE:msg_end_byte]

    signature = data[msg_end_byte:]

    return uuid, unicast_port, msg_type, msg_size, msg, signature

# Verify signature
def verifySignature(key, message, signature):
    h = SHA256.new(message)
    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        print("Signature is not valid")
        return False

# Sign a message
def sign(message, key):
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    return signature

class MulticastPeer:
    def __init__(self):
        # Networking init
        self.unicast_socket, self.multicast_socket = createSockets()
        self.unicast_port = self.unicast_socket.getsockname()[1]

        # Create reading threads
        read_unicast_thread = Thread(target=self.readUnicast, daemon=True)
        read_multicast_thread = Thread(target=self.readMulticast, daemon=True)

        read_multicast_thread.start()
        read_unicast_thread.start()

        # Peer specific init
        self.group_public_keys = {}
        self.uuid = str(uuid4())
        self.key_pair = RSA.generate(1024)
        self.public_key = self.key_pair.publickey()

        _public_key = self.public_key.export_key("PEM").decode("UTF-8")
        self.public_key_str = _public_key

        _public_key = addHeader(self.uuid, self.unicast_port, MSG_TYPE_PUBKEY, _public_key)

        # Send first message (public key)
        self.multicast_socket.sendto(_public_key, (MULTICAST_ADDR, PORT))
        print("Done initializing, entering group")
        print("Sending public key via MULTICAST")

    def readUnicast(self):
        while True:
            data, addr = self.unicast_socket.recvfrom(4096)
            # Ignore signature since its first time receiving msg
            uuid, unicast_port, msg_type, msg_size, msg, _ = parseBytesData(data)
            # The message sent is a public key
            if msg_type == MSG_TYPE_PUBKEY:
                # Add the new public key
                # Extract public key received
                key = RSA.import_key(msg)
                # Add new public
                self.group_public_keys[uuid] = key

    def readMulticast(self):
        while True:
            data, addr = self.multicast_socket.recvfrom(4096)
            uuid, unicast_port, msg_type, msg_size, msg, signature = parseBytesData(data)
            if uuid == self.uuid:
                continue
            # The message sent is a public key
            if msg_type == MSG_TYPE_PUBKEY:
                # New node entered the group and sent his public key
                # Add the new public key
                # Extract public key received
                key = RSA.import_key(msg)
                # Add new public
                self.group_public_keys[uuid] = key

                print("New node added")
                # The unicast address of the sender (new node)
                unicast_addr = (addr[0], unicast_port)

                # Make msg adding header to public key                
                msg_bytes = addHeader(self.uuid, self.unicast_port, MSG_TYPE_PUBKEY, self.public_key_str)
                # Send public key to new node in group
                self.unicast_socket.sendto(msg_bytes, unicast_addr)
                print("Sending public key via UNICAST to new node")
            # The message sent is a normal message
            elif msg_type == MSG_TYPE_NORMAL: 
                key = self.group_public_keys[uuid]
                # Verify signature
                if verifySignature(key, msg, signature):
                    print(f"[{uuid[:12]}]: {msg.decode('UTF-8')}")
                else:
                    print("Problem with signature")
            else:
                print(f"The message type {msg_type} is not valid.")
                exit()
def main():
    peer = MulticastPeer()
    try:
        while True:
            msg = input("Digite a mensagem: ")
            sig = sign(msg.encode("UTF-8"), peer.key_pair)
            msg_bytes = addHeader(peer.uuid, peer.unicast_port, MSG_TYPE_NORMAL, msg)
            msg_bytes += sig
            peer.multicast_socket.sendto(msg_bytes, (MULTICAST_ADDR, PORT))
    except KeyboardInterrupt:
        exit()   

if __name__ == "__main__":
    main()
