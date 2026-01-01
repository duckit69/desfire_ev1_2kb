from  desfire_ev1.desfire_ev1_card import DesfireCard
from  desfire_ev1.applications import ApplicationManager
from  desfire_ev1.files import FileManager
from ui.pic_codec import CardImageCodec
import cv2 

# Constants
MASTER_KEY = bytes([0x00] * 8)
MASTER_APP = [0x00, 0x00, 0x00]
KEY_ZERO = [0x00]
custom_application = [ [0x11, 0x11, 0x11], [0x11, 0x11, 0x12] ]


imageManager = CardImageCodec()

compressedVector, metaData = imageManager.compress("id_picture.jpg")

img = imageManager.decompress(compressedVector, metaData, "output.jpg", True)



