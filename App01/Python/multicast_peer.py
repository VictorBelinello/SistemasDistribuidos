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
        self.keyPair = crypto.getKeyPair()
        pubKey = self.keyPair.publickey()

        # Envia chave publica para grupo Multicast
        decodeKey = pubKey.export_key("PEM").decode("UTF-8")
        msg = self.addHeader(decodeKey, MSG_TYPE_PUBKEY)
        # Envia para grupo
        self.sock.sendto(msg.encode("UTF-8"), (MULTICAST_ADDR, PORT))

    def getInput(self):
        while True:
            msg = input("Digite a mensagem: ")
            self.sendMulticast(msg, "2")

    def addHeader(self, msg, msgType):
        # Obtem comprimento da mensagem e converte para string
        msgSize = str(len(msg))
        # zfill preenche com zeros a esquerda para que a string tenha tamanho final MAX_NUMBER_DIGITS_MSG
        msgSize = msgSize.zfill(MAX_NUMBER_DIGITS_MSG)
        # Adiciona header na msg
        msg = str(self.UUID) + msgType + msgSize + msg
        return msg

    def parseData(self, data):
        # Extrai os campos do datagrama recebido
        uuid = data[UUID_RANGE].decode("UTF-8")
        msgType = data[MSG_TYPE_RANGE].decode("UTF-8")
        msgSize = int(data[MSG_SIZE_RANGE].decode("UTF-8"))
        msg = data[MSG_START_BYTE:MSG_START_BYTE + msgSize]
        signStart = MSG_START_BYTE + msgSize
        signature = data[signStart:]
        return uuid, msgType, msg, signature

    # Envia uma mensagem assinada para grupo multicast
    def sendMulticast(self, msg, msgType):
        # Obtem assinatura da msg
        sig = crypto.sign(msg.encode("UTF-8"), self.keyPair)
        # Adiciona header na mensagem
        msg = self.addHeader(msg, msgType)
        # Combina mensagem e assinatura em bytes
        data = msg.encode("UTF-8") + sig
        # Envia para grupo
        self.sock.sendto(data, (MULTICAST_ADDR, PORT))

    def run(self):
        try:
            while True:
                # Recebe dados e endereço(do remetente) do socket
                data, addr = self.sock.recvfrom(MSG_MAX_CHAR)
                uuid, msgType, msg, signature = self.parseData(data)
                print(f"{self.UUID} recebi mensagem")
                if(msgType == MSG_TYPE_PUBKEY):
                    key = crypto.keyFromString(msg)
                    self.pubKeys[uuid] = key
                    print("Public Key added")
                else:
                    # Pega a chave publica do remetente
                    key = self.pubKeys[uuid]
                    if(crypto.verify(key, msg, signature)):
                        msg = msg.decode("UTF-8")
                        print(f"[{uuid}]: {msg}")
                    else:
                        print("Problema com assinatura")
        except Exception as e:
            print("Exception", e)
        