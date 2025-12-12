from smartcard.System import readers
from smartcard.util import toHexString
from .crypto import des_cbc_decrypt, des_cbc_encrypt, generate_reader_challenge, rotate_left

class DesfireCard:
    def __init__(self, reader_index=0):
        """Initialize connection to card"""
        r = readers()
        self.reader = r[reader_index]
        self.connection = self.reader.createConnection()
        self.connection.connect()
        print(f"Connected to: {self.reader}")
        print(f"ATR: {toHexString(self.connection.getATR())}")
    
    def transmit(self, apdu):
        """Send APDU and return response"""
        return self.connection.transmit(apdu)
    
    def get_version(self):
        """Get card version info (3 frames)"""
        apdu = [0x90, 0x60, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.transmit(apdu)
        
        frames = [data]
        while sw2 == 0xAF:
            apdu = [0x90, 0xAF, 0x00, 0x00, 0x00]
            data, sw1, sw2 = self.transmit(apdu)
            frames.append(data)
        
        return frames
    
    def select_application(self, aid):
        """Select application by AID"""
        apdu = [0x90, 0x5A, 0x00, 0x00, 0x03] + aid + [0x00]
        data, sw1, sw2 = self.transmit(apdu)
        return sw1 == 0x91 and sw2 == 0x00
    
    def authenticate(self, key_number, key_value):
        """Authenticate with DES key"""
        # Request challenge
        apdu = [0x90, 0x0A, 0x00, 0x00, 0x01] + key_number + [0x00]
        encrypted_challenge, sw1, sw2 = self.transmit(apdu)
        
        # Decrypt and rotate card challenge
        card_challenge = des_cbc_decrypt(bytes(encrypted_challenge), key_value)
        rotated = rotate_left(card_challenge, 1)
        
        # Generate reader challenge and combine
        reader_challenge = generate_reader_challenge()
        response_data = reader_challenge + rotated
        
        # Encrypt and send
        encrypted_response = des_cbc_encrypt(response_data, key_value)
        apdu = [0x90, 0xAF, 0x00, 0x00, 0x10] + list(encrypted_response) + [0x00]
        data, sw1, sw2 = self.transmit(apdu)
        
        return sw1 == 0x91 and sw2 == 0x00
    
    def format_card(self):
        """Format entire card (deletes everything)"""
        apdu = [0x90, 0xFC, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.transmit(apdu)
        return sw1 == 0x91 and sw2 == 0x00