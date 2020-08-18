from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

import ast
import sys
import socket
import struct
from threading import Thread, active_count
from uuid import uuid4

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
        print("ERROR: Signature is not valid")
        return False

# Sign a message
def sign(message, key):
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    return signature

# Print a message to terminal
def printMessage(header, message):
    print(f"[{header:^11}]: {message}")

class MulticastPeer:
    def __init__(self, multicast_addr):
        # Networking init
        self.multicast_addr = multicast_addr
        self.unicast_socket, self.multicast_socket = createSockets(self.multicast_addr)
        self.unicast_port = self.unicast_socket.getsockname()[1]

        # Create reading threads
        read_unicast_thread = Thread(target=self.readUnicast, daemon=True)
        read_multicast_thread = Thread(target=self.readMulticast, daemon=True)

        read_multicast_thread.start()
        read_unicast_thread.start()

        # Peer specific init
        self.group_public_keys = {}
        self.uuid = str(uuid4())[:UUID_SHORT]
        self.group_reputations = {self.uuid:1}
        self.key_pair = RSA.generate(1024)
        self.public_key = self.key_pair.publickey()

        _public_key = self.public_key.export_key("PEM").decode("UTF-8")
        self.public_key_str = _public_key

        _public_key = addHeader(self.uuid, self.unicast_port, MSG_TYPE_PUBKEY, _public_key)

        # Send first message (public key)
        self.multicast_socket.sendto(_public_key, (multicast_addr, PORT))
        # Print basic info about program
        print("*"*40)
        print("Done initializing, entering group.")
        print("The id of sender will be shown at the start of a message, between brackets '[]'.")
        print(f"Your id is: {self.uuid}")
        print("To report a message send by <id> just say: !<id>")
        print("To quit just say: !exit or press CTRL+C")
        print("*"*40)

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
            # The message sent contains a list of reputations of group 
            if msg_type == MSG_TYPE_REPUTATION:
                reputations = ast.literal_eval(msg.decode("UTF-8"))
                self.group_reputations.update(reputations)

    def readMulticast(self):
        while True:
            data, addr = self.multicast_socket.recvfrom(4096)
            uuid, unicast_port, msg_type, msg_size, msg, signature = parseBytesData(data)
            if uuid == self.uuid:
                continue
            print("\r") # Reset to start of line
            # The message sent is a public key
            if msg_type == MSG_TYPE_PUBKEY:
                # New node entered the group and sent his public key
                # Add the new public key
                # Extract public key received
                key = RSA.import_key(msg)
                # Add new public key
                self.group_public_keys[uuid] = key
                # Add new reputation, start at 1 = 100%
                self.group_reputations[uuid] = 1.0

                # The unicast address of the sender (new node)
                unicast_addr = (addr[0], unicast_port)

                # Make msg adding header to public key                
                msg_bytes = addHeader(self.uuid, self.unicast_port, MSG_TYPE_PUBKEY, self.public_key_str)
                # Send public key to new node in group
                self.unicast_socket.sendto(msg_bytes, unicast_addr)
                # Send list of reputation to node
                msg_bytes = addHeader(self.uuid, self.unicast_port, MSG_TYPE_REPUTATION, str(self.group_reputations))
                self.unicast_socket.sendto(msg_bytes, unicast_addr)
                printMessage("SYSTEM","New node added")
            # The message sent is a normal message
            elif msg_type == MSG_TYPE_NORMAL: 
                key = self.group_public_keys[uuid]
                # Verify signature
                if verifySignature(key, msg, signature):
                    printMessage(uuid, msg.decode('UTF-8'))
            # The message sent is a report of fake news
            elif msg_type == MSG_TYPE_REPORT:
                key = self.group_public_keys[uuid]
                # Verify signature
                if verifySignature(key, msg, signature):
                    reported = msg.decode('UTF-8')
                    if reported == self.uuid:
                        printMessage("WARNING", f"{uuid} reported YOU for sending fake news")
                    else: 
                        printMessage("WARNING", f"{uuid} reported {reported} for sending fake news")
                    self.decreaseReputationOf(reported)
            # The message sent is a peer leaving the group
            elif  msg_type == MSG_TYPE_LEFT:
                printMessage("SYSTEM", f"*{uuid}* left the group." )
                self.group_public_keys.pop(uuid)
                self.group_reputations.pop(uuid)
            else:
                print(f"ERROR: The message type {msg_type} is not valid.")
                exit()
            print("Enter message: ", end="") # Print again the message to get input
            sys.stdout.flush()

    def decreaseReputationOf(self, uuid):
        current_rep = float(self.group_reputations[uuid])
        new_rep = current_rep * 0.9 # 10% less reputation
        self.group_reputations[uuid] = new_rep

    def parseMessageToSend(self, msg):
        if msg[0] == "!":
            command = msg[1:]
            if command == "exit":
                return "", MSG_TYPE_LEFT
            elif command == "list":
                print("\rList of reputation on 0-1 scale:")
                for k, v in self.group_reputations.items():
                    v = str(float(v))
                    print(f"[{k}]: {v}")
                return msg, None
            else: # Report command
                # The user wrote the short version of uuid, but it is stored as long
                short_keys = [key[:UUID_SHORT]for key in self.group_reputations.keys()]
                uuid = command
                if uuid not in short_keys:
                    print("Invalid uuid, try again")
                    print(f"Members: {short_keys}")
                    return msg, None
                else:
                    return uuid, MSG_TYPE_REPORT
        else:
            return msg, MSG_TYPE_NORMAL 

def getMulticastAddress():
    if len(sys.argv) < 2:
        print("ERROR: You must pass the multicast IP")
        sys.exit(0)
    else:
        multicast_addr = sys.argv[1]
        try:
            r = socket.inet_aton(multicast_addr)
            if r < socket.inet_aton('224.0.0.0') or r > socket.inet_aton('239.255.255.255'):
                print("ERROR: Not valid multicast address")
                sys.exit(0)
            else:
                return multicast_addr
        except socket.error as e:
            print(f"ERROR {multicast_addr} is not a valid IP address")
            sys.exit(0)

def main():
    addr = getMulticastAddress()
    peer = MulticastPeer(addr)
    try:
        while True:
            msg = input("Enter message: ")
            msg, msg_type = peer.parseMessageToSend(msg)
            if msg_type == None: # The user executed a command that has a local result (like listing the reputation of nodes)
                continue    
            if msg_type == MSG_TYPE_LEFT: # No need to sign the message
                msg_bytes = addHeader(peer.uuid, peer.unicast_port, MSG_TYPE_LEFT, "")
                peer.multicast_socket.sendto(msg_bytes, (peer.multicast_addr, PORT))
                sys.exit(0)
            sig = sign(msg.encode("UTF-8"), peer.key_pair)
            msg_bytes = addHeader(peer.uuid, peer.unicast_port, msg_type, msg)
            msg_bytes += sig
            peer.multicast_socket.sendto(msg_bytes, (peer.multicast_addr, PORT))
            
    except KeyboardInterrupt:
        # Send the warning before leaving
        msg_bytes = addHeader(peer.uuid, peer.unicast_port, MSG_TYPE_LEFT, "")
        peer.multicast_socket.sendto(msg_bytes, (peer.multicast_addr, PORT))
        sys.exit(0)   

if __name__ == "__main__":
    main()
