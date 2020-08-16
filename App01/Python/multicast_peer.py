import socket
import struct
from threading import Thread
from uuid import uuid4

import crypto
from setup import *

class MulticastPeer(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.keepAlive = True

        # Network
        # Socket para IPv4, UDP(Datagramas)
        self.multicastSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.multicastSock.settimeout(0.2)
        self.unicastSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.unicastSock.settimeout(0.2)

        # Configuração para socket multicast (não tem uma classe especifica como em Java)
        membership = socket.inet_aton(
            MULTICAST_ADDR) + socket.inet_aton(BIND_ADDR)
        self.multicastSock.setsockopt(
            socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        self.multicastSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.multicastSock.bind((BIND_ADDR, PORT))

        # Configuração para socket unicast
        self.unicastSock.bind(('',0))
        addr, port = self.unicastSock.getsockname()
        self.unicastPort = port

        # Thread
        # Inicia thread de leitura de mensagens
        self.start()

        # Peer object
        self.pubKeys = {}
        # Obtem um uuid aleatorio
        self.UUID = str(uuid4())
        # Obtem par de chaves
        self.keyPair = crypto.getKeyPair()
        self.pubKey = self.keyPair.publickey()

        # Envia chave publica para grupo Multicast
        decodedKey = self.pubKey.export_key("PEM").decode("UTF-8")
        msg = self.addHeader(decodedKey, MSG_TYPE_PUBKEY)

        # Envia para grupo
        self.multicastSock.sendto(msg.encode("UTF-8"), (MULTICAST_ADDR, PORT))

        self.t = Thread(target=self.readUnicast)
        self.t.start()


    def readUnicast(self):
        while self.keepAlive:
            try:
                # Recebe o unicast dos membros do grupo
                data, addr = self.unicastSock.recvfrom(4096)
                uuid, uniPort, msgType, msg, signature = self.parseData(data)
                # Adiciona a chave publica dele na lista
                key = crypto.keyFromString(msg)
                self.pubKeys[uuid] = key
            except socket.timeout as e:
                continue

    def getInput(self):
        try:
            while True:
                msg = input("Digite a mensagem: ")
                self.sendMulticast(msg, MSG_TYPE_NORMAL)
        except KeyboardInterrupt:
            self.keepAlive = False
            
            self.t.join()
            self.join()

            self.unicastSock.close()
            self.multicastSock.close()

            exit()
        
    def addHeader(self, msg, msgType):
        # Obtem comprimento da mensagem e converte para string
        msgSize = str(len(msg))
        # zfill preenche com zeros a esquerda para que a string tenha tamanho final MAX_NUMBER_DIGITS_MSG
        msgSize = msgSize.zfill(MAX_NUMBER_DIGITS_MSG)
        # Obtem comprimento da porta(em digitos) unicast e converte para string
        portSize = len(str(self.unicastPort))
        # zfill novamente
        port = str(self.unicastPort).zfill(5) # 64k portas no maximo, 5 digitos serve
        # Adiciona header na msg
        msg = str(self.UUID) + port + msgType + msgSize + msg
        return msg

    def parseData(self, data):
        # Extrai os campos do datagrama recebido
        uuid = data[UUID_RANGE].decode("UTF-8")

        unicastPort = int(data[PORT_RANGE].decode("UTF-8"))

        msgType = data[MSG_TYPE_RANGE].decode("UTF-8")

        msgSize = int(data[MSG_SIZE_RANGE].decode("UTF-8"))

        msg = data[MSG_START_BYTE:MSG_START_BYTE + msgSize]

        signStart = MSG_START_BYTE + msgSize
        signature = data[signStart:]

        return uuid, unicastPort, msgType, msg, signature

    # Envia uma mensagem assinada para grupo multicast
    def sendMulticast(self, msg, msgType):
        # Obtem assinatura da msg
        sig = crypto.sign(msg.encode("UTF-8"), self.keyPair)
        # Adiciona header na mensagem
        msg = self.addHeader(msg, msgType)
        # Combina mensagem e assinatura em bytes
        data = msg.encode("UTF-8") + sig
        # Envia para grupo
        self.multicastSock.sendto(data, (MULTICAST_ADDR, PORT))

    # Envia uma mensagem unicast
    def sendUnicast(self, msg, msgType, addr):
        # Adiciona header na mensagem
        msg = self.addHeader(msg, msgType)
        # Envia msg para endereço especificado
        self.unicastSock.sendto(msg.encode("UTF-8"), addr)

    def run(self):
        while self.keepAlive:
            try:
                # Recebe dados e endereço(do remetente) do socket
                data, addr = self.multicastSock.recvfrom(MSG_MAX_CHAR)
                uuid, uniPort, msgType, msg, signature = self.parseData(data)
                if(uuid == self.UUID):
                    continue
                if(msgType == MSG_TYPE_PUBKEY):
                    # Novo nó entrou no grupo
                    # Adiciona a chave publica dele na lista
                    key = crypto.keyFromString(msg)
                    self.pubKeys[uuid] = key

                    # Pega a minha chave publica
                    decodedKey = self.pubKey.export_key("PEM").decode("UTF-8")
                    ip = addr[0] # Nos testes é sempre local, mas para ficar generico pega o ip remetente
                    uniAddr = (ip, uniPort)
                    # Envia chave publica via unicast
                    self.sendUnicast(decodedKey, MSG_TYPE_PUBKEY, uniAddr)
                    print("Public Key added")

                else:
                    # Pega a chave publica do remetente
                    key = self.pubKeys[uuid]
                    if(crypto.verify(key, msg, signature)):
                        msg = msg.decode("UTF-8")
                        print(f"[{uuid}]: {msg}")
                    else:
                        print("Problema com assinatura")
            except socket.timeout as e:
                continue
            
        