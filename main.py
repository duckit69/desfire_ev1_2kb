# main.py

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget)
from PyQt5.QtCore import Qt
from ui.source_interface import SourceInterface
from ui.destination_interface import DestinationInterface  # Add this import

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
        self.driver_app_id = [0x00, 0x00, 0x01]
        self.driver_file_id = 0x01
        self.driver_pic_file_id = 0x02
        
        # Mission related information
        self.mission_app_id = [0x00, 0x00, 0x02]
        self.mission_file_id = 0x01
        self.mission_file_size = 57
        
        # Articles related information
        self.article_app_id = [0x00, 0x00, 0x03]
        self.article_file_id = 0x01
        self.article_record_size = 8
        self.article_number = 50
        
        # Load from database
        self.articles_from_db = self.load_articles_from_database()
        self.trucks_from_db = self.load_trucks_from_database()
        self.missions_from_db = self.load_missions_from_database()  # Add this
        
        # Destination point (can be configured)
        self.destination_point = "djelfa"

        # Create central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Stacked widget to switch between interfaces
        self.stacked_widget = QStackedWidget()
        main_stack_layout = QVBoxLayout(central_widget)
        main_stack_layout.addWidget(self.stacked_widget)
        
        # Create base interface
        self.base_interface = self.create_base_interface()
        
        # Create source interface
        self.source_interface = SourceInterface(self.articles_from_db, self.trucks_from_db)
        self.source_interface.back_clicked.connect(self.show_base_interface)
        self.source_interface.form_submitted.connect(self.handle_form_data)
        
        # Create destination interface
        self.destination_interface = DestinationInterface(
            destination_point=self.destination_point,
            expected_missions=self.missions_from_db,
            card_manager=self.desfireCardManager,
            file_manager=self.fileManager
        )
        self.destination_interface.back_clicked.connect(self.show_base_interface)
        self.destination_interface.read_card_btn.clicked.connect(self.on_read_card_at_destination)
        self.destination_interface.card_validated.connect(self.handle_delivery_action)
        
        # Add interfaces to stacked widget
        self.stacked_widget.addWidget(self.base_interface)  # Index 0
        self.stacked_widget.addWidget(self.source_interface)  # Index 1
        self.stacked_widget.addWidget(self.destination_interface)  # Index 2
        
    def load_articles_from_database(self):
        """Load articles from your database"""
        # TODO: Replace with actual API call
        return [
            {"id": 1, "content": "AR01", "source": "Oran", "destination": "Chlef", "site_id": 1, "tag": 1, "site_type": 9},
            {"id": 2, "content": "AR02", "source": "Oran", "destination": "Chlef", "site_id": 1, "tag": 1, "site_type": 9},
            {"id": 3, "content": "AR03", "source": "Oran", "destination": "Chlef", "site_id": 1, "tag": 1, "site_type": 9},
            {"id": 4, "content": "AR04", "source": "Oran", "destination": "Chlef", "site_id": 1, "tag": 1, "site_type": 9},
        ]
        
    def load_trucks_from_database(self):
        """Load trucks from your database"""
        # TODO: Replace with actual API call
        return [
            {"id": 1, "model": "MR01", "license_plate": "TRCK1317", "available": "Free"},
            {"id": 2, "model": "MR02", "license_plate": "TRCK1317", "available": "Free"},
            {"id": 3, "model": "MR03", "license_plate": "TRCK1317", "available": "Free"},
            {"id": 4, "model": "MR04", "license_plate": "TRCK1317", "available": "Free"},
        ]
        
    def load_missions_from_database(self):
        """Load expected missions from database"""
        # TODO: Replace with actual API call
        return [
            {"mission_id": "MSN00001", "truck_id": "TRK00123", "source": "Oran", "destination": "djelfa", "status": "In Transit"},
            {"mission_id": "MSN00002", "truck_id": "TRK00456", "source": "Chlef", "destination": "djelfa", "status": "In Transit"},
            {"mission_id": "MSN00003", "truck_id": "TRK00789", "source": "Biskra", "destination": "djelfa", "status": "In Transit"},
            {"mission_id": "MSN00004", "truck_id": "TRK00999", "source": "Medya", "destination": "djelfa", "status": "In Transit"},
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
        
        # Connect buttons
        self.source_btn.clicked.connect(self.on_source_clicked)
        self.destination_btn.clicked.connect(self.on_destination_clicked)
        self.format_card_btn.clicked.connect(self.on_format_card_clicked)
        
        return base_widget
        
    def on_source_clicked(self):
        """Switch to source interface"""
        print("Source button clicked - switching to source interface")
        self.stacked_widget.setCurrentIndex(1)
        
    def on_destination_clicked(self):
        """Switch to destination interface"""
        print("Destination button clicked - switching to destination interface")
        # Reset destination interface before showing
        self.destination_interface.reset_interface()
        # Refresh missions before showing
        self.destination_interface.set_expected_missions(self.missions_from_db)
        self.stacked_widget.setCurrentIndex(2)
        
    def on_format_card_clicked(self):
        """Format the card"""
        print("Format Card button clicked")
        master_app_id = [0x00, 0x00, 0x00]
        self.desfireCardManager.select_application(master_app_id)
        self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
        self.desfireCardManager.format_card()
        print("Format is done")
        
    def show_base_interface(self):
        """Return to base interface"""
        print("Returning to base interface")
            # Reset destination interface when leaving
        if hasattr(self, 'destination_interface'):
            self.destination_interface.reset_interface()
        self.stacked_widget.setCurrentIndex(0)
        
    def on_read_card_at_destination(self):
        """Read card and validate at destination checkpoint"""
        try:
            print("Reading card at destination...")
            
            # Read mission data
            self.desfireCardManager.select_application(self.mission_app_id)
            self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
            mission_data = self.read_mission()
            
            # Read driver data
            self.desfireCardManager.select_application(self.driver_app_id)
            self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
            driver_data = self.read_driver_info()
            
            # Read driver photo
            #photo_data, photo_meta = self.read_compressed_image()
            #driver_data['photo_data'] = photo_data
            #driver_data['photo_meta'] = photo_meta
            
            # Read articles
            self.desfireCardManager.select_application(self.article_app_id)
            self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
            articles_data = self.read_all_articles()
            
            # Combine all card data
            card_data = {
                'mission': mission_data,
                'driver': driver_data,
                'articles': articles_data
            }
            
            # Validate and display
            self.destination_interface.validate_and_display_card(card_data)
            
        except Exception as e:
            print(f"Error reading card: {e}")
            self.destination_interface.status_label.setText(f"❌ Error reading card: {str(e)}")
            self.destination_interface.status_label.setStyleSheet("padding: 10px; font-size: 12px; color: red;")
        
    def handle_delivery_action(self, action_data):
        """Handle delivery approval or rejection"""
        action = action_data['action']
        data = action_data['data']
        
        print(f"Delivery {action}: {data['mission']['mission_id']}")
        
        if action == 'approved':
            # Update mission status to DELIVERED
            self.desfireCardManager.select_application(self.mission_app_id)
            self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
            self.update_mission_status(2)  # 2 = DELIVERED
            
            # TODO: Update database
            print("Mission marked as DELIVERED")
            
        elif action == 'rejected':
            # TODO: Handle rejection logic
            print("Mission rejected")
        
    def handle_form_data(self, data):
        """Process submitted form data from source interface"""
        self.applicationManager.create_application(self.driver_app_id)
        self.applicationManager.create_application(self.mission_app_id)
        self.applicationManager.create_application(self.article_app_id)

        # Write driver info
        self.desfireCardManager.select_application(self.driver_app_id)
        self.fileManager.create_standard_file(self.driver_file_id, 20)
        self.fileManager.create_standard_file(self.driver_pic_file_id, 1200)
        self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
        self.write_driver_infos(data['driver_name'], data['driver_license'])
        self.write_compressed_image(data['image_vec'], data['image_metaData'])
        print("Wrote Driver Info")

        # Write mission info
        self.desfireCardManager.select_application(self.mission_app_id)
        self.fileManager.create_standard_file(self.mission_file_id, 57)
        self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
        truck_id = data['truck']['license_plate'] if data['truck'] else "UNKNOWN"
        status = 0  # Pending
        self.write_mission_information(truck_id, status, data['source'], data['destination'])
        print(f"Wrote Mission info")
        
        # Write articles
        self.desfireCardManager.select_application(self.article_app_id)
        self.desfireCardManager.authenticate(self.key_number_zero, self.master_key_value)
        self.fileManager.create_linear_record_file(self.article_file_id, self.article_record_size, self.article_number)
        for article in data['articles']:
            self.write_article(article['content'][:4].upper(), int(article['quantity']))

        print("wrote articles infos")
    # === Helper functions ===
    
    def write_driver_infos(self, driver_name, driver_license):
        """Write driver information to card"""
        data = driver_name + driver_license
        byte_data = list(data.encode('utf-8'))
        self.fileManager.write_data(self.driver_file_id, 0, byte_data)
        
    def read_driver_info(self):
        """Read driver info from card"""
        data = self.fileManager.read_data(self.driver_file_id, 0, 20)
        info_str = bytes(data).decode('utf-8').strip()
        # Assume format: first 10 chars = name, rest = license
        name = info_str[:10].strip()
        license = info_str[10:].strip()
        return {'name': name, 'license': license}

    def write_compressed_image(self, data, meta):
        """Write compressed image to card"""
        meta_json = json.dumps(meta).encode('utf-8')
        meta_len = len(meta_json)
        
        meta_len_bytes = [meta_len & 0xFF, (meta_len >> 8) & 0xFF, (meta_len >> 16) & 0xFF, (meta_len >> 24) & 0xFF]
        payload = meta_len_bytes + list(meta_json) + list(data)
        
        offset = 0
        chunk_size = 47
        while offset < len(payload):
            end = min(offset + chunk_size, len(payload))
            chunk = payload[offset:end]
            self.fileManager.write_data(self.driver_pic_file_id, offset=offset, data=chunk)
            offset += len(chunk)
        
        return offset
    
    def read_compressed_image(self):
        """Read compressed image from card"""
        header = self.fileManager.read_data(self.driver_pic_file_id, offset=0, length=4)
        meta_len = header[0] | (header[1] << 8) | (header[2] << 16) | (header[3] << 24)
        
        meta_bytes = self.fileManager.read_data(self.driver_pic_file_id, offset=4, length=meta_len)
        meta = json.loads(bytes(meta_bytes).decode('utf-8'))
        
        data_offset = 4 + meta_len
        data_length = 994
        data = self.fileManager.read_data(self.driver_pic_file_id, offset=data_offset, length=data_length)
        
        return bytes(data), meta

    def write_mission_information(self, truck_id, status, source, destination):
        """Write mission info to card"""
        mission_id = "MSN00001"  # TODO: Get from API
        
        mission_data = list(mission_id.ljust(8, ' ').encode('utf-8')[:8])
        truck_data = list(truck_id.ljust(8, ' ').encode('utf-8')[:8])
        source_data = list(source.ljust(20, ' ').encode('utf-8')[:20])
        destination_data = list(destination.ljust(20, ' ').encode('utf-8')[:20])
        
        complete_data = mission_data + truck_data + [status] + source_data + destination_data
        
        print(f"Complete data length: {len(complete_data)} bytes")
        
        # Split into two chunks: first 47 bytes, then remaining
        chunk1 = complete_data[:47]  # Bytes 0-46 (47 bytes)
        chunk2 = complete_data[47:]  # Bytes 47-56 (10 bytes)
        
        print(f"Chunk 1 (47 bytes): {chunk1}")
        print(f"Chunk 2 ({len(chunk2)} bytes): {chunk2}")
        
        # Write first chunk at offset 0
        self.fileManager.write_data(self.mission_file_id, offset=0, data=chunk1)
        print(f"Written chunk 1: 47 bytes at offset 0")
        
        # Write second chunk at offset 47
        self.fileManager.write_data(self.mission_file_id, offset=47, data=chunk2)
        print(f"Written chunk 2: {len(chunk2)} bytes at offset 47")
        
        print(f"Mission written: {mission_id}")
        return mission_id

    def update_mission_status(self, new_status):
        """Update mission status"""
        self.fileManager.write_data(self.mission_file_id, 16, [new_status])
        print(f"Status updated to: {new_status}")

    def read_mission(self):
        """Read mission data from card"""
        data = self.fileManager.read_data(self.mission_file_id, 0, self.mission_file_size)
        
        mission_id = bytes(data[0:8]).decode('utf-8').strip()
        truck_id = bytes(data[8:16]).decode('utf-8').strip()
        status = data[16]
        source = bytes(data[17:37]).decode('utf-8').strip()
        destination = bytes(data[37:57]).decode('utf-8').strip()
        
        status_names = {0: "Pending", 1: "In Transit", 2: "Delivered"}
        
        return {
            'mission_id': mission_id,
            'truck_id': truck_id,
            'status': status_names.get(status, 'Unknown'),
            'source': source,
            'destination': destination
        }
    
    def write_article(self, code, quantity):
        """Write article record"""
        from desfire_ev1.utils import to_4bytes
        code_data = list(code.ljust(4, ' ').encode('utf-8')[:4])
        quantity_data = to_4bytes(quantity)
        record_data = code_data + quantity_data
        self.fileManager.write_record(self.article_file_id, 0, record_data)
        self.fileManager.commit_transaction()
        
    def read_all_articles(self):
        """Read all articles from card"""
        from desfire_ev1.utils import from_4bytes
        data = self.fileManager.read_records(self.article_file_id, 0, 0)
        
        articles = []
        for i in range(0, len(data), self.article_record_size):
            if i + self.article_record_size <= len(data):
                record = data[i:i+self.article_record_size]
                code = bytes(record[0:4]).decode('utf-8').strip()
                quantity = from_4bytes(record[4:8])
                articles.append({'code': code, 'quantity': quantity})
        
        return articles


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
