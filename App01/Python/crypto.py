from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def getKeys():
    key = RSA.generate(1024)
    return key

def sign(message, key):
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    return signature

def verify(key, message, signature):
    h = SHA256.new(message)
    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        print("Signature is not valid")
        return False