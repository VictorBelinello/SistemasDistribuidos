import socket
import struct
from uuid import uuid4
from threading import Thread

import crypt


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
        self.pubKeys = {}
        # Obtem um uuid aleatorio
        self.UUID = uuid4()
        # Obtem par de chaves 
        self.keyPair = crypt.getKeys()
        # Adiciona chave publica
        self.pubKeys[str(self.UUID)] = self.keyPair.publickey()
        

    def getInput(self):
        while True:
            msg = input("Digite a mensagem: ")
            self.sendMulticast(msg)

    # Envia msg para grupo multicast
    def sendMulticast(self, msg):
        # Obtem assinatura da msg
        sig = crypt.sign(msg.encode("UTF-8"), self.keyPair)
        # Adiciona header na msg
        msg = str(self.UUID) + msg 
        # Combina mensagem e assinatura em bytes
        data = msg.encode("UTF-8") + sig
        # Envia para grupo
        self.sock.sendto(data, (multicast_addr, port))        

    def run(self):
        while True:
            # Recebe dados e endereço(do remetente) do socket
            data, addr = self.sock.recvfrom(255)
            # Extrai o UUID do remetente
            senderID = data[:36].decode('UTF-8')
            # Obtem chave publica
           # pubKey = pubKeys[senderID]
            # Extrai mensagem 
            msg = data[36:36+5] # TODO: deixar generico, so funciona com msg = Teste
            # Extra assinatura da mensagem
            sig = bytes(data[36+5:])

            # Verifica assinatura
            #if(crypt.verify(pubKey, msg, sig)):
            #    print("Deu boa")
            print(f"\n[{senderID}]: {msg.decode()}\n")
           # else:
           #     print("Nao deu boa")