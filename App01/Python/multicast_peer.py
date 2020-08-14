import socket
import struct
from threading import Thread
from uuid import uuid4

import crypto
from setup import *

class MulticastPeer(Thread):

    def __init__(self):
        Thread.__init__(self)

        # Network
        # Socket para IPv4, UDP(Datagramas)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Configuração para socket multicast (não tem uma classe especifica como em Java)
        membership = socket.inet_aton(
            MULTICAST_ADDR) + socket.inet_aton(BIND_ADDR)
        self.sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((BIND_ADDR, PORT))

        # Thread
        # Inicia thread de leitura de mensagens
        self.start()

        # Peer object
        self.pubKeys = {}
        # Obtem um uuid aleatorio
        self.UUID = uuid4()
        # Obtem par de chaves
        self.keyPair = crypto.getKeys()
        pubKey = self.keyPair.publickey()

        # Adiciona chave publica
        self.pubKeys[str(self.UUID)] = pubKey

        # Envia chave publica para grupo Multicast
        self.sendMulticast("Teste", "0")
        #self.sendMulticast(str(pubKey), "0")
        exit(0)

    def getInput(self):
        while True:
            msg = input("Digite a mensagem: ")
            self.sendMulticast(msg)

    def addHeader(self, msg, msgType):
        # Obtem comprimento da mensagem e converte para string
        msgSize = str(len(msg))
        # zfill preenche com zeros a esquerda para que a string tenha tamanho final MAX_NUMBER_DIGITS_MSG
        msgSize = msgSize.zfill(MAX_NUMBER_DIGITS_MSG)
        # Adiciona header na msg
        msg = str(self.UUID) + msgType + msgSize + msg
        print(f"UUID:{msg[UUID_RANGE]}\nType:{msg[MSG_TYPE_RANGE]}\nLenght:{msg[MSG_LENGHT_RANGE]}\nMessage:{msg[MSG_START_BYTE:]}")
        return msg

    # Envia msg para grupo multicast
    def sendMulticast(self, msg, msgType):
        # Obtem assinatura da msg
        sig = crypto.sign(msg.encode("UTF-8"), self.keyPair)

        msg = self.addHeader(msg, msgType)
        exit(0)
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
            # TODO: deixar generico, so funciona com msg = Teste
            msg = data[36:]
            # Extra assinatura da mensagem
            sig = bytes(data[36+5:])

            # Verifica assinatura
            # if(crypt.verify(pubKey, msg, sig)):
            #    print("Deu boa")
            print(f"\n[{senderID}]: {msg.decode()}\n")
           # else:
           #     print("Nao deu boa")
