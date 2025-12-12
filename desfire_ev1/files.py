from smartcard.util import toHexString
from desfire_ev1.utils import to_3bytes, to_4bytes, from_4bytes

class FileManager:
    def __init__(self, card):
        """Initialize with DesfireCard instance"""
        self.card = card
    
    def list_files(self):
        """List all file IDs in current application"""
        apdu = [0x90, 0x6F, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        
        if sw1 == 0x91 and sw2 == 0x00:
            file_ids = list(data)
            print(f"Files: {[f'0x{fid:02X}' for fid in file_ids]}")
            return file_ids
        return []
    
    def delete_file(self, file_id):
        """Delete file"""
        apdu = [0x90, 0xDF, 0x00, 0x00, 0x01, file_id, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Delete file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    # Standard File
    def create_standard_file(self, file_id, file_size, comm_settings=0x00, access_rights=[0x00, 0x00]):
        """Create standard data file"""
        size_bytes = to_3bytes(file_size)
        apdu = [0x90, 0xCD, 0x00, 0x00, 0x07, file_id, comm_settings] + access_rights + size_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create standard file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def write_data(self, file_id, offset, data):
        """Write data to standard file"""
        offset_bytes = to_3bytes(offset)
        length_bytes = to_3bytes(len(data))
        apdu = [0x90, 0x3D, 0x00, 0x00, 7 + len(data), file_id] + offset_bytes + length_bytes + data + [0x00]
        response, sw1, sw2 = self.card.transmit(apdu)
        print(f"Write to file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def read_data(self, file_id, offset, length):
        """Read data from standard file"""
        offset_bytes = to_3bytes(offset)
        length_bytes = to_3bytes(length)
        apdu = [0x90, 0xBD, 0x00, 0x00, 0x07, file_id] + offset_bytes + length_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Read from file {file_id} - Status: {sw1:02X} {sw2:02X}")
        print(f"Data: {bytes(data).decode('utf-8', errors='ignore')}")
        return data
    
    # Value File
    def create_value_file(self, file_id, lower_limit, upper_limit, initial_value, limited_credit=False, comm_settings=0x00, access_rights=[0x00, 0x00]):
        """Create value file"""
        lower_bytes = to_4bytes(lower_limit)
        upper_bytes = to_4bytes(upper_limit)
        initial_bytes = to_4bytes(initial_value)
        limited = 0x01 if limited_credit else 0x00
        apdu = [0x90, 0xCC, 0x00, 0x00, 0x11, file_id, comm_settings] + access_rights + lower_bytes + upper_bytes + initial_bytes + [limited, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create value file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def credit_value(self, file_id, amount):
        """Add value"""
        amount_bytes = to_4bytes(amount)
        apdu = [0x90, 0x0C, 0x00, 0x00, 0x05, file_id] + amount_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Credit {amount} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def debit_value(self, file_id, amount):
        """Subtract value"""
        amount_bytes = to_4bytes(amount)
        apdu = [0x90, 0xDC, 0x00, 0x00, 0x05, file_id] + amount_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Debit {amount} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def get_value(self, file_id):
        """Read current value"""
        apdu = [0x90, 0x6C, 0x00, 0x00, 0x01, file_id, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        if sw1 == 0x91 and sw2 == 0x00:
            value = from_4bytes(data)
            print(f"Value: {value}")
            return value
        return None
    
    # Record Files
    def create_linear_record_file(self, file_id, record_size, max_records, comm_settings=0x00, access_rights=[0x00, 0x00]):
        """Create linear record file"""
        size_bytes = to_3bytes(record_size)
        max_bytes = to_3bytes(max_records)
        apdu = [0x90, 0xC1, 0x00, 0x00, 0x0A, file_id, comm_settings] + access_rights + size_bytes + max_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create linear record file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def create_cyclic_record_file(self, file_id, record_size, max_records, comm_settings=0x00, access_rights=[0x00, 0x00]):
        """Create cyclic record file"""
        size_bytes = to_3bytes(record_size)
        max_bytes = to_3bytes(max_records)
        apdu = [0x90, 0xC0, 0x00, 0x00, 0x0A, file_id, comm_settings] + access_rights + size_bytes + max_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create cyclic record file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def write_record(self, file_id, offset, data):
        """Write record"""
        offset_bytes = to_3bytes(offset)
        length_bytes = to_3bytes(len(data))
        apdu = [0x90, 0x3B, 0x00, 0x00, 7 + len(data), file_id] + offset_bytes + length_bytes + data + [0x00]
        response, sw1, sw2 = self.card.transmit(apdu)
        print(f"Write record - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def read_records(self, file_id, record_offset, num_records):
        """Read records"""
        offset_bytes = to_3bytes(record_offset)
        num_bytes = to_3bytes(num_records)
        apdu = [0x90, 0xBB, 0x00, 0x00, 0x07, file_id] + offset_bytes + num_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Read records - Status: {sw1:02X} {sw2:02X}")
        print(f"Data: {bytes(data).decode('utf-8', errors='ignore')}")
        return data
    
    def clear_record_file(self, file_id):
        """Clear all records"""
        apdu = [0x90, 0xEB, 0x00, 0x00, 0x01, file_id, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Clear records - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def commit_transaction(self):
        """Validate all pending writes in current application"""
        apdu = [0x90, 0xC7, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.transmit(apdu)
        print(f"Commit transaction - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00

    def abort_transaction(self):
        """Cancel all pending writes in current application"""
        apdu = [0x90, 0xA7, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.transmit(apdu)
        print(f"Abort transaction - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
