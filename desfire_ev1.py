from smartcard.System import readers
from smartcard.util import toHexString
from Crypto.Cipher import DES 
from Crypto.Random import get_random_bytes
import random
# default_key = 00 00 00 00 00 00 00 00
# master application id = 00 00 00 
# App ID is 3 bytes 

"""
Typical work flow:
1-Authenticate to master app
2-Create custom application
3-Select custom application
4-Authenticate to custom app
5-Create file
6-Write data to file
"""

master_key = bytes([0x00] * 8)
master_app_id = [0x00, 0x00, 0x00, 0x00]
key_number_zero = [0x00] 


print(f"Master key: {master_key}")

# list readers
def list_readers():
    r = readers()
    return r


# 0 for contactless ---- 1 for contacted 
def connect_to_reader_by_type(nmb):
    readers_list = list_readers()
    reader = readers_list[nmb]
    connection = reader.createConnection()
    connection.connect()

    print(f"Connected to card in reader: {reader}")
    print(f"ATR: {toHexString(connection.getATR())}")

    return connection

connection = connect_to_reader_by_type(0)

def print_additional_frames(connection, sw2):
    while sw2 == 0XAF:
        apdu = [0x90, 0xAF, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(apdu)
        print(f"Response: {toHexString(data)}")
        print(f"Status: {sw1:02X} {sw2:02X}")

def get_desfire_ev1_version(nmb):
    apdu = [0x90, 0x60, 0x00, 0x00, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    print(f"Response: {toHexString(data)}")
    print(f"Status: {sw1:02X} {sw2:02X}")
    if sw2 == 0XAF:
        print_additional_frames(connection, sw2)

def select_app(connection, appid):
    apdu = [0x90, 0x5A, 0x00, 0x00, 0x03] + appid + [0x00]
    
    data, sw1, sw2 = connection.transmit(apdu)
    return data, sw1, sw2




def des_cbc_encrypt(data, key, iv=bytes(8)): # Purpose: Encrypts data using DES algorithm in CBC (Cipher Block Chaining) mode
    # data: Plaintext to encrypt
    # key: Encryption key (8 bytes for DES)
    # iv: Initialization Vector (defaults to 8 null bytes)

    cipher = DES.new(key, DES.MODE_CBC, iv=iv) # Create DES cipher in CBC mode with given IV

    # CBC Mode: Each block of plaintext is XORed with the previous ciphertext block before encryption
    # IV (Initialization Vector): Ensures identical plaintexts produce different ciphertexts

    if len(data) % 8 != 0:
        data = data + bytes(8 - len(data) % 8) # Pad data to 8-byte blocks (DES requirement)
    return cipher.encrypt(data) # Return encrypted data

def des_cbc_decrypt(data, key, iv=bytes(8)):
    cipher = DES.new(key, DES.MODE_CBC, iv=iv)
    return cipher.decrypt(data)


def authenticate_des_key(key):
    apdu = [0x90, 0x0A, 0x00, 0x00, 0x01] + key + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    """
    print(f"Challenge from card: {toHexString(data)}")
    print(f"Status: {sw1:02X} {sw2:02X}")
    """
    return data


def authenticate(connection, appid, key_number, key_value):
    select_app(connection, appid)
    # Start authentication with key 0x00 (master key) position number 0 ( keys are ranging from 0 - 13)
    
    # Get challenge from card
    encrypted_challenge = authenticate_des_key(key_number)

    # Decrypt card's challenge
    card_challenge = des_cbc_decrypt(bytes(encrypted_challenge), key_value)

    # Rotate card challenge left by 1 byte 
    rotated_card_challenge = card_challenge[1:] + card_challenge[0:1]

    # Generate reader_challenge
    reader_challenge = bytes([random.randint(0, 255) for _ in range(8)])  # b'\x00\x00\x00\x00\x00\x00\x00\x00'

    # add reader challenge + rotated_card_challenge
    response_data = reader_challenge + rotated_card_challenge

    # Encrypt and send response
    encrypted_response = des_cbc_encrypt(response_data, key_value)

    apdu = [0x90, 0xAF, 0x00, 0x00, 0x10] + list(encrypted_response) + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Auth response: {toHexString(data)}")
    print(f"Status: {sw1:02X} {sw2:02X}")

def list_applications(connection):
    # Do not require auth with master app
    # Get application IDs command
    apdu = [0x90, 0x6A, 0x00, 0x00, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Status: {sw1:02X} {sw2:02X}")
    
    if sw1 == 0x91 and sw2 == 0x00:
        # Parse AIDs (3 bytes each)
        aids = []
        for i in range(0, len(data), 3):
            aid = data[i:i+3]
            aids.append(aid)
            print(f"Application: {toHexString(aid)}")
        return aids
    return []

def delete_application(connection, aid):
    # deletion requires auth with master app
    apdu = [0x90, 0xDA, 0x00, 0x00, 0x03] + aid + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    print(f"Delete {toHexString(aid)} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00


# authenticate(connection, master_app_id, key_number_zero, master_key)


def create_application(connection, aid):
    key_permissions = 0x0F  # Default settings
    total_keys = 0x01      # 1 DES key
    
    apdu = [0x90, 0xCA, 0x00, 0x00, 0x05] + aid + [key_permissions, total_keys, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Data: {data} - Create app {toHexString(aid)} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00


list_applications(connection)
aid = [0x12, 0x34, 0x56]
#create_application(connection, aid)
#list_applications(connection)




# Files part
# 1- select app
data, sw1, sw2 = select_app(connection, aid)
print(f"Data: {data} - app {toHexString(aid)} - Status: {sw1:02X} {sw2:02X}")

# auth with app
authenticate(connection, aid, key_number_zero, master_key)


authenticate(connection, master_app_id, key_number_zero, master_key)
delete_application(connection, aid)