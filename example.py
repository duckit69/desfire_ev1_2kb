from  desfire_ev1.desfire_ev1_card import DesfireCard
from  desfire_ev1.applications import ApplicationManager
from  desfire_ev1.files import FileManager

# Constants
MASTER_KEY = bytes([0x00] * 8)
MASTER_APP = [0x00, 0x00, 0x00]
KEY_ZERO = [0x00]
custom_application = [ [0x11, 0x11, 0x11], [0x11, 0x11, 0x12] ]
# Connect to card
card = DesfireCard(reader_index=0)

# Initialize managers
app_mgr = ApplicationManager(card)
file_mgr = FileManager(card)

# Authenticate to master app
card.select_application(MASTER_APP)
card.authenticate(KEY_ZERO, MASTER_KEY)

# Create application
# 0x0B Force user to authenticate before managing files
app_mgr.create_application(custom_application[0], 0x0B)

card.select_application(custom_application[0])
ok = card.authenticate(KEY_ZERO, MASTER_KEY)

if not ok:
    print("Auth failed, cannot manage files")
else:
    print("Auth Successed, you can manage files")

# Create value file
file_mgr.list_files()

file_mgr.delete_file(0x03)



"""
# Select and authenticate to custom app
card.select_application(custom_application[0])
card.authenticate(KEY_ZERO, MASTER_KEY)

# Create file and write data
file_mgr.create_standard_file(0x01, 32)
file_mgr.write_data(0x01, 0, list(b"Hello DESFIRE!"))
file_mgr.read_data(0x01, 0, 14)
"""