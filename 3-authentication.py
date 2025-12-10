from smartcard.CardMonitoring import CardMonitor, CardObserver
# Smart card communication library (PC/SC)

import random
# Generate random numbers for authentication challenges

from Crypto.Cipher import DES
# DES encryption/decryption functions


class MyObserver(CardObserver): #watches for card events
    def __init__(self):
        self.keys = [bytes([0x00] * 8)]  # Stores the DES key (all zeros - default DESFire key)
    
    def update(self, observable, actions): # Called automatically when card is inserted/removed
        (addedcards, removedcards) = actions # Unpacks the card events tuple
        for card in addedcards: 
            # For each newly inserted card, call handle_card()
            self.handle_card(card) 
    
    def handle_card(self, card):
        connection = card.createConnection() # Create communication channel to the card
        try:
            connection.connect() # Establish physical connection
            self.authenticate_with_cbc_mode(connection) # Authentication process


        except Exception as e:
            print(f"Error: {e}")
        finally:
            connection.disconnect()

    def des_cbc_encrypt(self, data, key, iv=bytes(8)): # Purpose: Encrypts data using DES algorithm in CBC (Cipher Block Chaining) mode
        # data: Plaintext to encrypt
        # key: Encryption key (8 bytes for DES)
        # iv: Initialization Vector (defaults to 8 null bytes)


        cipher = DES.new(key, DES.MODE_CBC, iv=iv) # Create DES cipher in CBC mode with given IV

        # CBC Mode: Each block of plaintext is XORed with the previous ciphertext block before encryption
        # IV (Initialization Vector): Ensures identical plaintexts produce different ciphertexts

        if len(data) % 8 != 0:
            data = data + bytes(8 - len(data) % 8) # Pad data to 8-byte blocks (DES requirement)
        return cipher.encrypt(data) # Return encrypted data

    def des_cbc_decrypt(self, data, key, iv=bytes(8)):
        cipher = DES.new(key, DES.MODE_CBC, iv=iv)
        return cipher.decrypt(data)

    def rotate_left(self, data):
        # Rotate bytes left - security feature to prevent replay attacks
        return data[1:] + data[0:1]

    def authenticate_with_cbc_mode(self, connection):
        # Select PICC level
        SELECT_PICC_APDU = [0x90, 0x5A, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00]
        response, sw1, sw2 = connection.transmit(SELECT_PICC_APDU)
        if sw1 != 0x91 or sw2 != 0x00:
            return False
        
        key = self.keys[0]
        
        # Initiate authentication
        AUTH_INIT_APDU = [0x90, 0x1A, 0x00, 0x00, 0x01, 0x00, 0x00] # APDU command to select card application level
        response, sw1, sw2 = connection.transmit(AUTH_INIT_APDU) # Send command, get response + status words
        
        if sw1 != 0x91 or sw2 != 0xAF: # Check if selection was successful
            return False
        
        encrypted_rndB = response
        
        try:
            # Step 1: Decrypt RndB using CBC mode with zero IV
            rndB = self.des_cbc_decrypt(bytes(encrypted_rndB), key, iv=bytes(8))
            print("key B recieved: ",rndB)
            # Step 2: Generate RndA
            rndA = bytes([random.randint(0, 255) for _ in range(8)])
            print("key A r: ",rndA)
            # Step 3: Rotate RndB and combine with RndA
            rndB_rot = self.rotate_left(rndB)
            rndAB = rndA + rndB_rot
            print("key AB = rndA + rndB_rot: ",rndA)
            # Step 4: Encrypt RndAB using CBC mode with encrypted RndB as IV
            rndAB_enc = self.des_cbc_encrypt(rndAB, key, iv=bytes(encrypted_rndB))
            
            # Step 5: Send authentication response
            AUTH_RESPONSE_APDU = [0x90, 0xAF, 0x00, 0x00, 0x10] + list(rndAB_enc) + [0x00]
            response, sw1, sw2 = connection.transmit(AUTH_RESPONSE_APDU)
            
            if sw1 == 0x91 and sw2 == 0x00:
                # Verify mutual authentication
                if len(response) == 8:
                    encrypted_rndA = response
                    decrypted_rndA = self.des_cbc_decrypt(bytes(encrypted_rndA), key, iv=rndAB_enc[-8:])
                    expected_rndA_rot = self.rotate_left(rndA)
                    
                    if decrypted_rndA == expected_rndA_rot:
                        print("✓ Authenticated")    
                        return True
                return True
            return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

def main():
    cardmonitor = CardMonitor()
    cardobserver = MyObserver()
    cardmonitor.addObserver(cardobserver)

    print("DESFire Authentication - Waiting for card...")
    
    try:
        while True:
            try:
                input()
                break
            except EOFError:
                import time
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cardmonitor.deleteObserver(cardobserver)

if __name__ == "__main__":
    main()