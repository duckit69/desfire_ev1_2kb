from smartcard.System import readers
from smartcard.util import toHexString
from Crypto.Cipher import DES 
from Crypto.Random import get_random_bytes
import random


from desfire_ev1.utils import to_4bytes, to_3bytes, from_4bytes
# default_key = 00 00 00 00 00 00 00 00
# master application id = 00 00 00 
# App ID is 3 bytes 

"""
Typical work flow:
1-Authenticate to app
2-Create custom application
3-Select custom application
4-Authenticate to custom app
5-Create file
6-Write data to file
"""

master_key = bytes([0x00] * 8)
key_number_zero = [0x00] 

master_app_id = [0x00, 0x00, 0x00]
aid1 = [0x11, 0x11, 0x11]
aid2 = [0x11, 0x11, 0x12]
aid3 = [0x11, 0x11, 0x13]
aid4 = [0x11, 0x11, 0x14]

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

def print_additional_frames(connection, sw2):
    while sw2 == 0XAF:
        apdu = [0x90, 0xAF, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(apdu)
        print(f"Data (text): {bytes(data).decode('utf-8', errors='ignore')}")

        #print(f"Response: {toHexString(data)}")
        #print(f"Status: {sw1:02X} {sw2:02X}")

def get_desfire_ev1_version(connection):
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
    
    return data, sw1, sw2

def authenticate(connection, appid, key_number, key_value):
    # Start authentication with key 0x00 (master key) position number 0 ( keys are ranging from 0 - 13)
    # Get challenge from card
    encrypted_challenge, sw1, sw2 = authenticate_des_key(key_number)

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

def list_files(connection):
    # Get file IDs command
    apdu = [0x90, 0x6F, 0x00, 0x00, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Status: {sw1:02X} {sw2:02X}")
    
    if sw1 == 0x91 and sw2 == 0x00:
        file_ids = list(data)
        print(f"Files in application: {[f'0x{fid:02X}' for fid in file_ids]}")
        print(f"Total files: {len(file_ids)}")
        return file_ids
    return []

def create_application(connection, aid):
    key_permissions = 0x0F  # Default settings
    total_keys = 0x01      # 1 DES key
    
    apdu = [0x90, 0xCA, 0x00, 0x00, 0x05] + aid + [key_permissions, total_keys, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Data: {data} - Create app {toHexString(aid)} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def delete_application(connection, aid):
    # deletion requires auth with master app
    apdu = [0x90, 0xDA, 0x00, 0x00, 0x03] + aid + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    print(f"Delete {toHexString(aid)} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

#list_applications(connection)


def delete_file(connection, file_id):
    apdu = [0x90, 0xDF, 0x00, 0x00, 0x01, file_id, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Delete file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def create_standard_file(connection, aid,file_id, file_size):
    
    select_app(connection, aid)
    authenticate(connection, aid, key_number_zero, master_key)
    communication_settings = 0x00  # Plain communication ---- TAKES 1 BYTES
    access_rights = [0x00, 0x00]   # [0x00 0x00] Key 0 required for all operations ***** [0XEE 0xEE]Free access (no auth needed) ---- TAKES 2 BYTES

    byte1 = file_size & 0xFF
    byte2 = (file_size >> 8) & 0xFF # we are shifting 8 bits from the original value to find the second byte
    byte3 = (file_size >> 16) & 0xFF # we are shifting 16 bits from the original value to find the third byte
    file_size_bytes = [byte1, byte2, byte3]   # ---- TAKES 3 BYTES

    #       1Byte  //    //    //    //     //          //                      2Bytes          3BYTES
    apdu = [0x90, 0xCD, 0x00, 0x00, 0x07, file_id, communication_settings] + access_rights + file_size_bytes + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Create file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

# Convert values to 4 bytes each (little-endian, signed 32-bit)
def to_4bytes(value):
    return [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF]

def create_value_file(connection, file_id, lower_limit, upper_limit, initial_value, limited_credit_enabled):
    communication_settings = 0x00  # Plain communication
    access_rights = [0x00, 0x00]   # Key 0 required for all operations
    
    lower_bytes = to_4bytes(lower_limit) # minimum allowed value
    upper_bytes = to_4bytes(upper_limit) # maximum allowed value
    initial_bytes = to_4bytes(initial_value) # starting value
    # Sets limited credit mode:  0x00 = Disabled (normal): credit operations cannot exceed upper_limit
    # 0x01 = Enabled: allows temporary exceeding of upper_limit (requires commit/abort transaction) For simple use, set to False (disabled).
    limited_credit = 0x01 if limited_credit_enabled else 0x00 
      
    apdu = [0x90, 0xCC, 0x00, 0x00, 0x11, file_id, communication_settings] + access_rights + lower_bytes + upper_bytes + initial_bytes + [limited_credit, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Create value file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def write_data_in_standard_file(connection, file_id, offset, data):
    """
    Docstring for write_data_in_standard_file
    
    :param connection: connection object
    :param file_id: id where we want to write 
    :param offset: where to start writing 
    :param data: data to be written
    """
    data_length = len(data)
    
    # Offset as 3 bytes (little-endian)
    offset_bytes = [offset & 0xFF, (offset >> 8) & 0xFF, (offset >> 16) & 0xFF]
    
    # Length as 3 bytes (little-endian)
    length_bytes = [data_length & 0xFF, (data_length >> 8) & 0xFF, (data_length >> 16) & 0xFF]
    
    apdu = [0x90, 0x3D, 0x00, 0x00, 7 + data_length, file_id] + offset_bytes + length_bytes + data + [0x00]
    response, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Write to file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00


def read_data_in_standard_file(connection, file_id, offset, length):
    # Offset as 3 bytes
    offset_bytes = [offset & 0xFF, (offset >> 8) & 0xFF, (offset >> 16) & 0xFF]
    
    # Length as 3 bytes (little-endian)
    length_bytes = [length & 0xFF, (length >> 8) & 0xFF, (length >> 16) & 0xFF]
    
    apdu = [0x90, 0xBD, 0x00, 0x00, 0x07, file_id] + offset_bytes + length_bytes + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Read from file {file_id} - Status: {sw1:02X} {sw2:02X}")
    print(f"Data (hex): {toHexString(data)}")
    print(f"Data (text): {bytes(data).decode('utf-8', errors='ignore')}")
    
    return data

def create_value_file(connection, file_id, lower_limit, upper_limit, initial_value, limited_credit_enabled):
    communication_settings = 0x00  # Plain communication
    access_rights = [0x00, 0x00]   # Key 0 required for all operations
        
    lower_bytes = to_4bytes(lower_limit) # minimum allowed value
    upper_bytes = to_4bytes(upper_limit) # maximum allowed value
    initial_bytes = to_4bytes(initial_value) # starting value
    limited_credit = 0x01 if limited_credit_enabled else 0x00 # Sets limited credit mode:  0x00 = Disabled (normal): credit operations cannot exceed upper_limit
                                                              # 0x01 = Enabled: allows temporary exceeding of upper_limit (requires commit/abort transaction) For simple use, set to False (disabled).
    
    apdu = [0x90, 0xCC, 0x00, 0x00, 0x11, file_id, communication_settings] + access_rights + lower_bytes + upper_bytes + initial_bytes + [limited_credit, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Create value file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def get_value(connection, file_id):
    apdu = [0x90, 0x6C, 0x00, 0x00, 0x01, file_id, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Get value from file {file_id} - Status: {sw1:02X} {sw2:02X}")
    
    if sw1 == 0x91 and sw2 == 0x00:
        # Convert 4 bytes (little-endian) to integer
        value = data[0] | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)
        print(f"Current value: {value}")
        return value
    return None

def commit_transaction(connection):
    # Saves all pending changes permanently Required whith creadit/debit with value file
    apdu = [0x90, 0xC7, 0x00, 0x00, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Commit transaction - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def abort_transaction(connection):
    # Cancels all pending changes, rolls back to previous state
    apdu = [0x90, 0xA7, 0x00, 0x00, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Abort transaction - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def credit_value(connection, file_id, amount):
    # Amount as 4 bytes (little-endian)
    amount_bytes = [amount & 0xFF, (amount >> 8) & 0xFF, (amount >> 16) & 0xFF, (amount >> 24) & 0xFF]
    
    apdu = [0x90, 0x0C, 0x00, 0x00, 0x05, file_id] + amount_bytes + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    

    print(f"Credit {amount} to file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def debit_value(connection, file_id, amount):
    # Amount as 4 bytes (little-endian)
    amount_bytes = [amount & 0xFF, (amount >> 8) & 0xFF, (amount >> 16) & 0xFF, (amount >> 24) & 0xFF]
    
    apdu = [0x90, 0xDC, 0x00, 0x00, 0x05, file_id] + amount_bytes + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Debit {amount} from file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def create_linear_record_file(connection, file_id, record_size, max_records):
    communication_settings = 0x00  # Plain communication
    access_rights = [0x00, 0x00]   # Key 0 required for all operations
    
    # Record size as 3 bytes (little-endian)
    record_size_bytes = [record_size & 0xFF, (record_size >> 8) & 0xFF, (record_size >> 16) & 0xFF]
    
    # Max records as 3 bytes (little-endian)
    max_records_bytes = [max_records & 0xFF, (max_records >> 8) & 0xFF, (max_records >> 16) & 0xFF]
    
    apdu = [0x90, 0xC1, 0x00, 0x00, 0x0A, file_id, communication_settings] + access_rights + record_size_bytes + max_records_bytes + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Create linear record file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def create_cyclic_record_file(connection, file_id, record_size, max_records):
    communication_settings = 0x00  # Plain communication
    access_rights = [0x00, 0x00]   # Key 0 required for all operations
    
    # Record size as 3 bytes (little-endian)
    record_size_bytes = [record_size & 0xFF, (record_size >> 8) & 0xFF, (record_size >> 16) & 0xFF]
    
    # Max records as 3 bytes (little-endian)
    max_records_bytes = [max_records & 0xFF, (max_records >> 8) & 0xFF, (max_records >> 16) & 0xFF]
    
    apdu = [0x90, 0xC0, 0x00, 0x00, 0x0A, file_id, communication_settings] + access_rights + record_size_bytes + max_records_bytes + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Create cyclic record file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def write_record(connection, file_id, offset, data):
    data_length = len(data)
    
    # Offset as 3 bytes (little-endian)
    offset_bytes = [offset & 0xFF, (offset >> 8) & 0xFF, (offset >> 16) & 0xFF]
    
    # Length as 3 bytes (little-endian)
    length_bytes = [data_length & 0xFF, (data_length >> 8) & 0xFF, (data_length >> 16) & 0xFF]
    
    apdu = [0x90, 0x3B, 0x00, 0x00, 7 + data_length, file_id] + offset_bytes + length_bytes + data + [0x00]
    response, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Write record to file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00

def read_records(connection, file_id, record_offset, num_records):
    # Record offset as 3 bytes (little-endian)
    offset_bytes = [record_offset & 0xFF, (record_offset >> 8) & 0xFF, (record_offset >> 16) & 0xFF]
    
    # Number of records as 3 bytes (little-endian)
    num_bytes = [num_records & 0xFF, (num_records >> 8) & 0xFF, (num_records >> 16) & 0xFF]
    
    apdu = [0x90, 0xBB, 0x00, 0x00, 0x07, file_id] + offset_bytes + num_bytes + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Read records from file {file_id} - Status: {sw1:02X} {sw2:02X}")
    print(f"Data (hex): {toHexString(data)}")
    print(f"Data (text): {bytes(data).decode('utf-8', errors='ignore')}")
    
    return data

def read_all_records(connection, file_id):
    # Use 0x000000 for offset and length to read ALL records
    offset_bytes = [0x00, 0x00, 0x00]
    num_bytes = [0x00, 0x00, 0x00]  # 0x000000 = read all
    
    apdu = [0x90, 0xBB, 0x00, 0x00, 0x07, file_id] + offset_bytes + num_bytes + [0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Read all records from file {file_id} - Status: {sw1:02X} {sw2:02X}")
    print(f"Data (hex): {toHexString(data)}")
    print(f"Data (text): {bytes(data).decode('utf-8', errors='ignore')}")

    print_additional_frames(connection, sw2)
    
    return data

def clear_record_file(connection, file_id):
    apdu = [0x90, 0xEB, 0x00, 0x00, 0x01, file_id, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Clear record file {file_id} - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00


def format_card(connection):
    # Must authenticate to master app first
    apdu = [0x90, 0xFC, 0x00, 0x00, 0x00]
    data, sw1, sw2 = connection.transmit(apdu)
    
    print(f"Format card - Status: {sw1:02X} {sw2:02X}")
    return sw1 == 0x91 and sw2 == 0x00




connection = connect_to_reader_by_type(0)

list_applications(connection)

select_app(connection, aid1)

authenticate(connection, aid1, key_number_zero, master_key)

list_files(connection)