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
#app_mgr.create_application(custom_application[0], 0x0B)

app_mgr.list_applications()

card.select_application(custom_application[0])
ok = card.authenticate(KEY_ZERO, MASTER_KEY)

if not ok:
    print("Auth failed, cannot manage files")
else:
    print("Auth Successed, you can manage files")

