def to_3bytes(value):
    """Convert integer to 3-byte little-endian list"""
    return [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF]

def to_4bytes(value):
    """Convert integer to 4-byte little-endian list"""
    return [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF]

def from_4bytes(byte_list):
    """Convert 4-byte little-endian list to integer"""
    return byte_list[0] | (byte_list[1] << 8) | (byte_list[2] << 16) | (byte_list[3] << 24)
