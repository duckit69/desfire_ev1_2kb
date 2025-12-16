def to_3bytes(value):
    """Convert integer to 3-byte little-endian list"""
    return [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF]

def to_4bytes(value):
    """Convert integer to 4-byte little-endian list"""
    return [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF]

def from_4bytes(byte_list):
    """Convert 4-byte little-endian list to integer"""
    return byte_list[0] | (byte_list[1] << 8) | (byte_list[2] << 16) | (byte_list[3] << 24)





"""

        print("=== Received Form Data ===")
        driver_name = data['driver_name']
        driver_license = data['driver_license']
        data = driver_name + driver_license
        response = self.applicationManager.create_application(self.driver_app_id)
        self.desfireCardManager.select_application(self.driver_app_id)
        # FIKHATER YACINE KHIER M MESSILA DRIVER 
        self.fileManager.create_standard_file(self.driver_file_id, 20)
        self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
        byte_data = list(data.encode('utf-8'))
        response = self.fileManager.write_data(self.driver_file_id, 0, byte_data)

"""