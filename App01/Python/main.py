import ast
import sys
from threading import Thread
from uuid import uuid4

from util import *

class MulticastPeer:
    def __init__(self, multicast_addr):
        self.initNetwork(multicast_addr)
        
        self.initThread()

        self.initPeer()
        
        # Send first message(the public key) to multicast group
        self.sendMulticast(self.public_key, MSG_TYPE_PUBKEY)

        # Print basic info about program
        self.printProgramInfo()

    def initNetwork(self, addr):
        # Save multicast address
        self.multicast_addr = addr
        # Create unicast and multicast sockets
        self.unicast_socket, self.multicast_socket = createSockets(self.multicast_addr)
        # Get unicast port
        self.unicast_port = self.unicast_socket.getsockname()[1]

    def initThread(self):
        # Create thread to read unicast messages
        # daemon=True allows the main program to exit
        read_unicast_thread = Thread(target=self.readUnicast, daemon=True)
        # Create thread to read multicast messages
        read_multicast_thread = Thread(target=self.readMulticast, daemon=True)

        # Start threads
        read_multicast_thread.start()
        read_unicast_thread.start()

    def initPeer(self):
        # Dict to save the pairs (uuid:public_key) of nodes
        self.group_public_keys = {}
        # Identifier of node, just for simplicity slices the original saving only UUID_SHORT chars
        self.uuid = str(uuid4())[:UUID_SHORT]
        # Dict to save the pairs (uuid:reputation) of nodes
        # Start putting itself with initial reputation of 1.0
        self.group_reputations = {self.uuid:1.0}
        # Generate the 1024bits RSA key 
        key_pair = RSA.generate(1024)
        # Get the matching RSA public key
        public_key = key_pair.publickey()
        # Store the public key as an UTF-8 string
        self.public_key = public_key.export_key().decode("UTF-8")
        # Create the scheme to sign messages
        self.signature_scheme = pkcs1_15.new(key_pair)

    def sendUnicast(self, message, message_type, address):
        # Send a unicast message
        # Only used and responding to new node
        message_bytes = self.addHeader(message, message_type)
        self.unicast_socket.sendto(message_bytes, address)

    def sendMulticast(self, message, message_type):
        # Send a multicast message
        # Only used for the first or when the message itself isn't important
        message_bytes = self.addHeader(message, message_type)
        self.multicast_socket.sendto(message_bytes, (self.multicast_addr, PORT))

    def sendMulticastSigned(self, message, message_type):
        # Send a signed multicast message
        message_hash = SHA256.new(message.encode("UTF-8"))
        try:
            signature = self.signature_scheme.sign(message_hash)
            message_bytes = self.addHeader(message, message_type)
            message_bytes = message_bytes + signature
            self.multicast_socket.sendto(message_bytes, (self.multicast_addr, PORT))
        except (ValueError, TypeError):
            printMessage("ERROR", "Signature is not valid")

    def printProgramInfo(self):
        print("*"*40)
        print("Done initializing, entering group.")
        print("The id of sender will be shown at the start of a message, between brackets '[]'.")
        print(f"Your id is: {self.uuid}")
        print("To report a message send by <id> just say: !<id>")
        print("To quit just say: !exit or press CTRL+C")
        print("*"*40)

    def parseInputMessage(self, msg):
        # Messages that start with ! are commands
        if msg[0] == "!":
            command = msg[1:]
            # Command to quit the program
            if command == "exit":
                # No need to send a message so msg=""
                return "", MSG_TYPE_EXIT
            # Command to list the nodes and reputation
            elif command == "list":
                # There is alreaddy an "Enter message: " on the terminal so use \r to reset the cursor
                print("\rList of reputation on 0 to 1 scale:")
                for uuid, value in self.group_reputations.items():
                    reputation = str( float(value) )
                    printMessage(uuid, reputation)
                # No need to send a message or type of message since it has "local" result
                return "", None
            # Command to report fake news
            else:
                # Just for better readability
                uuid = command 
                # If invalid uuid                 
                if uuid not in self.group_reputations:
                    printMessage("SYSTEM", "No node found with given id, try again.")
                    # Again no need to send message or type since it was an invalid id
                    return "", None
                # Valid uuid
                else:
                    # The message type REPORT expect the reported uuid inside it
                    return uuid, MSG_TYPE_REPORT
        else:
            return msg, MSG_TYPE_NORMAL

    def addHeader(self, message, message_type):
        if type(message) is not str:
            assert("The message on header should be of type str")

        # Make a fixed lenght(filled with zeros) string containing the size of message
        message_size = "{:05}".format(len(message))
        # Make a fixed lenght(filled with zeros) string containing the unicast port
        port = "{:05}".format(self.unicast_port)
        # Make header
        header = self.uuid + port + message_type + message_size
        # Add header to message
        message = header + message
        # Return message in bytes format
        return message.encode("UTF-8")

    def getInputLoop(self):
        try:
            while True:
                input_message = input("Enter message: ")
                msg, msg_type = self.parseInputMessage(input_message)
                # The user executed a command that has a local result (like listing the reputation of nodes)
                if msg_type == None:
                    continue
                # The user want to exit the program
                if msg_type == MSG_TYPE_EXIT:
                    msg_bytes = self.addHeader(msg, msg_type)
                    self.multicast_socket.sendto(msg_bytes, (self.multicast_addr, PORT))
                    sys.exit(0)
                # The user has a meaningful message
                # The user is reporting other node
                if msg_type == MSG_TYPE_REPORT:
                    # Adjust reputation internally, since loopback messages are ignored
                    self.decreaseReputationOf(msg)
                self.sendMulticastSigned(msg, msg_type)
        except KeyboardInterrupt:
            msg = ""
            self.sendMulticast(msg, MSG_TYPE_EXIT)
            sys.exit(0)

    def readUnicast(self):
        while True:
            data, addr = self.unicast_socket.recvfrom(4096)
            # Extract sender uuid, unicast port, type of message, size and message itself 
            uuid, unicast_port, msg_type, msg_size, msg, _ = parseBytesData(data)

            # The nodes already in group send their public key via UNICAST to new node
            if msg_type == MSG_TYPE_PUBKEY:
                # Extract public key received
                key = RSA.import_key(msg)
                # Add new public
                self.group_public_keys[uuid] = key
            
            # The message sent contains a list of reputations of group 
            if msg_type == MSG_TYPE_REPUTATION:
                # Convert the string in dict
                reputations = ast.literal_eval(msg.decode("UTF-8"))
                self.group_reputations.update(reputations)

    def readMulticast(self):
        while True:
            # Get bytes sent and address(IP, PORT) of sender
            data, addr = self.multicast_socket.recvfrom(4096)
            # Extract sender uuid, unicast port, type of message, size, message itself and signature of message
            uuid, unicast_port, msg_type, msg_size, msg, signature = parseBytesData(data)

            # Ignore loopback messages
            if uuid == self.uuid:
                continue

            # New node entered the group and sent his public key via MULTICAST
            if msg_type == MSG_TYPE_PUBKEY:
                # Extract public key received
                key = RSA.import_key(msg)
                # Add new public key
                self.group_public_keys[uuid] = key
                # Add new reputation, start at 1 = 100%
                self.group_reputations[uuid] = 1.0

                # The unicast address of the new node
                unicast_addr = (addr[0], unicast_port)

                # Send public key to new node
                self.sendUnicast(self.public_key, MSG_TYPE_PUBKEY, unicast_addr)
                # Send list of reputations to node
                self.sendUnicast(str(self.group_reputations), MSG_TYPE_REPUTATION, unicast_addr)

                printMessage("SYSTEM","New node added")

            # The message sent is a normal message
            elif msg_type == MSG_TYPE_NORMAL: 
                # Find the public key of sender
                key = self.group_public_keys[uuid]
                # Verify signature
                if verifySignature(key, msg, signature):
                    message = msg.decode("UTF-8")
                    printMessage(uuid, message)
            
            # The message sent is a report of fake news
            elif msg_type == MSG_TYPE_REPORT:
                # Find the public key of sender
                key = self.group_public_keys[uuid]
                # Verify signature
                if verifySignature(key, msg, signature):
                    reported = msg.decode('UTF-8')
                    # Print the warning message based on whether you are the reported node or not
                    if reported == self.uuid:
                        printMessage("WARNING", f"{uuid} reported YOU for sending fake news")
                    else: 
                        printMessage("WARNING", f"{uuid} reported {reported} for sending fake news")
                    # Adjust the reputation of reported node
                    self.decreaseReputationOf(reported)

            # The message sent is a nodde leaving the group
            elif msg_type == MSG_TYPE_EXIT:
                printMessage("SYSTEM", f"*{uuid}* left the group." )
                # Remove the node from the lists
                self.group_public_keys.pop(uuid)
                self.group_reputations.pop(uuid)
            # Invalid message type
            else:
                print(f"ERROR: The message type {msg_type} is not valid.")
                exit()
            print("Enter message: ", end="") # Print again the message to get input
            sys.stdout.flush()

    def decreaseReputationOf(self, uuid):
        current_rep = float(self.group_reputations[uuid])
        new_rep = current_rep * 0.9 # 10% less reputation
        self.group_reputations[uuid] = new_rep

def getMulticastAddress():
    if len(sys.argv) < 2:
        print("ERROR: You must pass the multicast IP")
        sys.exit(0)
    else: # Passed multicast ip 
        multicast_addr = sys.argv[1]
        try: # Verify if really is an IP address
            r = socket.inet_aton(multicast_addr)
            # Verify if is a multicast IP address
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
    peer.getInputLoop()

if __name__ == "__main__":
    main()
