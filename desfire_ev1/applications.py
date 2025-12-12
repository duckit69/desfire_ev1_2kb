from smartcard.util import toHexString

class ApplicationManager:
    def __init__(self, card):
        """Initialize with DesfireCard instance"""
        self.card = card
    
    def list_applications(self):
        """List all application IDs"""
        apdu = [0x90, 0x6A, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        
        if sw1 == 0x91 and sw2 == 0x00:
            aids = [data[i:i+3] for i in range(0, len(data), 3)]
            for aid in aids:
                print(f"Application: {toHexString(aid)}")
            return aids
        return []
    
    def create_application(self, aid, key_settings=0x0F, num_keys=0x01):
        """Create new application"""
        apdu = [0x90, 0xCA, 0x00, 0x00, 0x05] + aid + [key_settings, num_keys, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create app {toHexString(aid)} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def delete_application(self, aid):
        """Delete application"""
        apdu = [0x90, 0xDA, 0x00, 0x00, 0x03] + aid + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Delete {toHexString(aid)} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def change_key_settings(self, new_settings):
        """Change PICC key settings"""
        apdu = [0x90, 0x54, 0x00, 0x00, 0x01, new_settings, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Change key settings - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
