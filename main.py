# main.py

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget)
from PyQt5.QtCore import Qt
from ui.source_interface import SourceInterface

from desfire_ev1.applications import ApplicationManager
from desfire_ev1.files import FileManager
from desfire_ev1.desfire_ev1_card import DesfireCard
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Manager Interface")
        self.setGeometry(100, 100, 600, 600)
        # Initialize app file card managers
        self.desfireCardManager = DesfireCard() 
        self.applicationManager = ApplicationManager(self.desfireCardManager)
        self.fileManager = FileManager(self.desfireCardManager)
        # key numbers
        self.key_number_zero = [0x00]
        self.master_key_value = bytes([0x00] * 8)
        # application ids 
        # 0x00 0x00 0x01 Driver application 0x01 fileId information ( name + license)
        self.driver_app_id = [0x00, 0x00, 0x01]
        self.driver_file_id = 0x01
        self.driver_pic_file_id = 0x02
        # Load articles/trucks from database
        self.articles_from_db = self.load_articles_from_database()
        self.trucks_from_db = self.load_trucks_from_database()

        # Create central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Stacked widget to switch between interfaces
        self.stacked_widget = QStackedWidget()
        main_stack_layout = QVBoxLayout(central_widget)
        main_stack_layout.addWidget(self.stacked_widget)
        
        # Create base interface
        self.base_interface = self.create_base_interface()
        
        # Create source interface with articles database
        self.source_interface = SourceInterface(self.articles_from_db, self.trucks_from_db)
        self.source_interface.back_clicked.connect(self.show_base_interface)
        self.source_interface.form_submitted.connect(self.handle_form_data)
        
        # Add both interfaces to stacked widget
        self.stacked_widget.addWidget(self.base_interface)
        self.stacked_widget.addWidget(self.source_interface)
        
    def load_articles_from_database(self):
        """Load articles from your database - replace with actual DB call"""
        # TODO: Replace with actual database query
        # api call here to retrieve all articles
        return [
            {
            "id": 1,
            "content": "EarPhones",
            "source": "Oran",
            "destination": "Chlef",
            "site_id": 1,
            "tag": 1,
            "site_type": 9
            },
                        {
            "id": 2,
            "content": "Laptop Dell XPS",
            "source": "Oran",
            "destination": "Chlef",
            "site_id": 1,
            "tag": 1,
            "site_type": 9
            },
                        {
            "id": 3,
            "content": "Mouse Logitech MX",
            "source": "Oran",
            "destination": "Chlef",
            "site_id": 1,
            "tag": 1,
            "site_type": 9
            },
                        {
            "id": 4,
            "content": "Keyboard Mechanical",
            "source": "Oran",
            "destination": "Chlef",
            "site_id": 1,
            "tag": 1,
            "site_type": 9
            },
        ]

        
    def create_base_interface(self):
        """Create the original base interface"""
        base_widget = QWidget()
        main_layout = QVBoxLayout(base_widget)
        
        # First line: Two buttons
        first_line_layout = QHBoxLayout()
        
        self.source_btn = QPushButton("Source")
    def load_trucks_from_database(self):
        """Load trucks from your database - replace with actual DB call"""
        # TODO: Replace with actual database query
        # api call here to retrieve all trucks
        return [
            {
                "id": 1,
                "model": "Master Renault1",
                "license_plate": "5555-213-17",
                "available": "Free"
            },
            {
                "id": 2,
                "model": "Master Renault2",
                "license_plate": "5555-213-17",
                "available": "Free"
            },
            {
                "id": 3,
                "model": "Master Renault3",
                "license_plate": "5555-213-17",
                "available": "Free"
            },
            {
                "id": 4,
                "model": "Master Renault4",
                "license_plate": "5555-213-17",
                "available": "Free"
            },
        ]
        
    def create_base_interface(self):
        """Create the original base interface"""
        base_widget = QWidget()
        main_layout = QVBoxLayout(base_widget)
        
        # First line: Two buttons
        first_line_layout = QHBoxLayout()
        
        self.source_btn = QPushButton("Source")
        self.destination_btn = QPushButton("Destination")
        
        first_line_layout.addWidget(self.source_btn)
        first_line_layout.addWidget(self.destination_btn)
        
        # Second line: Format Card button
        second_line_layout = QHBoxLayout()
        
        self.format_card_btn = QPushButton("Format Card")
        second_line_layout.addWidget(self.format_card_btn)
        
        # Add both lines to main layout
        main_layout.addLayout(first_line_layout)
        main_layout.addLayout(second_line_layout)
        
        # Connect buttons to functions
        self.source_btn.clicked.connect(self.on_source_clicked)
        self.destination_btn.clicked.connect(self.on_destination_clicked)
        self.format_card_btn.clicked.connect(self.on_format_card_clicked)
        
        return base_widget
        
    def on_source_clicked(self):
        """Switch to source interface"""
        print("Source button clicked - switching to source interface")
        self.stacked_widget.setCurrentIndex(1)
        
    def on_destination_clicked(self):
        print("Destination button clicked")
        
    def on_format_card_clicked(self):
        print("Format Card button clicked")
        master_app_id = [0x00, 0x00, 0x00]
        self.desfireCardManager.select_application(master_app_id)
        self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
        self.desfireCardManager.format_card()
        print("Format is done")
        
    def show_base_interface(self):
        """Return to base interface"""
        print("Returning to base interface")
        self.stacked_widget.setCurrentIndex(0)
        
    def handle_form_data(self, data):
        """Process submitted form data"""
        # data recieved here will be written in the card
        self.applicationManager.create_application(self.driver_app_id)
        self.desfireCardManager.select_application(self.driver_app_id)
        self.fileManager.create_standard_file(self.driver_file_id, 20)
        self.fileManager.create_standard_file(self.driver_pic_file_id, 1200)
        self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
        self.write_driver_infos(self.driver_file_id, data['driver_name'], data['driver_license'])
        self.write_compressed_image(self.driver_pic_file_id, data['image_vec'], data['image_metaData'])
        
        # TODO: Save to database, process, etc.

    def write_driver_infos(self, file_id, driver_name, driver_license):
        data = driver_name + driver_license
        byte_data = list(data.encode('utf-8'))
        self.fileManager.write_data(self.driver_file_id, 0, byte_data)

    def write_compressed_image(self, file_id, data, meta):
        # Serialize metadata
        meta_json = json.dumps(meta).encode('utf-8')
        meta_len = len(meta_json)
        
        # Pack: [meta_length (4 bytes)] + [meta_json] + [data]
        meta_len_bytes = [
            meta_len & 0xFF,
            (meta_len >> 8) & 0xFF,
            (meta_len >> 16) & 0xFF,
            (meta_len >> 24) & 0xFF
        ]
        
        payload = meta_len_bytes + list(meta_json) + list(data)
        total_bytes = len(payload)
        offset = 0
        chunk_num = 1
        
        chunk_size = 47
        while offset < total_bytes:
            # Get chunk (last chunk may be smaller)
            end = min(offset + chunk_size, total_bytes)
            chunk = payload[offset:end]
            chunk_len = len(chunk)
            
            # Write chunk at current offset
            print(f"Writing chunk {chunk_num}: {chunk_len} bytes at offset {offset}")
            self.fileManager.write_data(file_id, offset=offset, data=chunk)
            
            # Update offset for next chunk
            offset += chunk_len
            chunk_num += 1

        print(f"Write complete: {offset} bytes written")
        return offset
    
    def read_compressed_image(self, file_id):
        # Read header (4 bytes)
        header = self.fileManager.read_data(file_id, offset=0, length=4)
        meta_len = header[0] | (header[1] << 8) | (header[2] << 16) | (header[3] << 24)
        
        # Read metadata
        meta_bytes = self.fileManager.read_data(file_id, offset=4, length=meta_len)
        meta = json.loads(bytes(meta_bytes).decode('utf-8'))
        
        # Read data (rest of file after metadata)
        data_offset = 4 + meta_len
        # You may want to store data length in meta for dynamic reading
        data_length = 994  # Known length
        data = self.fileManager.read_data(file_id, offset=data_offset, length=data_length)
        
        return bytes(data), meta

        # Read
        #data, meta = read_compressed_image(file_mgr, 0x01)
# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
