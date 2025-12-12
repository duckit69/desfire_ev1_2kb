from Crypto.Cipher import DES
import random

def des_cbc_encrypt(data, key, iv=bytes(8)):
    """Encrypt data using DES in CBC mode"""
    cipher = DES.new(key, DES.MODE_CBC, iv=iv)
    if len(data) % 8 != 0:
        data = data + bytes(8 - len(data) % 8)
    return cipher.encrypt(data)

def des_cbc_decrypt(data, key, iv=bytes(8)):
    """Decrypt data using DES in CBC mode"""
    cipher = DES.new(key, DES.MODE_CBC, iv=iv)
    return cipher.decrypt(data)

def generate_reader_challenge():
    """Generate random 8-byte challenge"""
    return bytes([random.randint(0, 255) for _ in range(8)])

def rotate_left(data, n=1):
    """Rotate bytes left by n positions"""
    return data[n:] + data[:n]
