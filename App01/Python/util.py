import socket
import struct

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from constants import *


# Create multicast and unicast sockets
def createSockets(multicast_addr):
    # Multicast socket
    # Datagram socket for IPv4
    multi_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Allow for address reuse (same machine same addr)
    multi_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # To join multicast group change the option IP_ADD_MEMBERSHIP, a 8-byte representation of:
    # multicast group address + network interface to listen
    membership = struct.pack("=4sL", socket.inet_aton(multicast_addr), socket.INADDR_ANY)
    multi_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    # Bind socket to all interfaces
    addr = ('0.0.0.0', PORT)
    multi_socket.bind(addr)

    # Unicast socket
    uni_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # If port = 0 a random available port is assigned
    addr = ('', 0)
    uni_socket.bind(addr)

    return uni_socket, multi_socket

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
        print("ERROR: Signature is not valid")
        return False

# Print a message to terminal
def printMessage(header, message):
    print(f"\r[{header:^11}]: {message}")

