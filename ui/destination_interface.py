# destination_interface.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QFormLayout, 
                             QTableWidget, QTableWidgetItem, QTextEdit,
                             QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from .pic_codec import CardImageCodec, HashManager


class DestinationInterface(QWidget):
    # Signal to go back to main interface
    back_clicked = pyqtSignal()
    card_validated = pyqtSignal(dict)  # Signal when card is successfully validated

    def __init__(self, destination_point="djelfa", expected_missions=None):
        super().__init__()
        self.destination_point = destination_point
        self.expected_missions = expected_missions if expected_missions else []
        self.image_processor = CardImageCodec()
        self.hashManager = HashManager()
        self.current_card_data = None
        
        self.init_ui()
        self.load_expected_missions()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Back button at the top
        back_btn = QPushButton("← Back")
        back_btn.setMaximumWidth(100)
        back_btn.clicked.connect(self.on_back_clicked)
        main_layout.addWidget(back_btn)
        
        # === Destination Point Label ===
        destination_label = QLabel(f"Destination: {self.destination_point}")
        destination_label.setStyleSheet("font-weight: bold; font-size: 16px; padding: 10px;")
        destination_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(destination_label)
        
        # === Box 1: Expected Missions ===
        self.missions_box = QGroupBox("Expected Missions")
        missions_layout = QVBoxLayout()
        
        self.missions_table = QTableWidget()
        self.missions_table.setColumnCount(3)
        self.missions_table.setHorizontalHeaderLabels(["Mission ID", "Truck ID", "Source"])
        self.missions_table.horizontalHeader().setStretchLastSection(True)
        self.missions_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        missions_layout.addWidget(self.missions_table)
        self.missions_box.setLayout(missions_layout)
        main_layout.addWidget(self.missions_box)
        
        # === Card Reading Section ===
        self.card_section = QGroupBox("Card Validation")
        card_layout = QVBoxLayout()
        
        # Read card button
        self.read_card_btn = QPushButton("Read Card")
        self.read_card_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-size: 14px;")
        self.read_card_btn.clicked.connect(self.on_read_card)
        card_layout.addWidget(self.read_card_btn)
        
        # Status message
        self.status_label = QLabel("Waiting for card...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; font-size: 12px;")
        card_layout.addWidget(self.status_label)
        
        self.card_section.setLayout(card_layout)
        main_layout.addWidget(self.card_section)
        
        # === Box 2: Card Information (hidden by default) ===
        self.card_info_box = QGroupBox("Card Information")
        self.card_info_box.setVisible(False)
        card_info_layout = QVBoxLayout()
        
        # Mission details
        mission_details_layout = QFormLayout()
        self.mission_id_label = QLabel("-")
        self.truck_id_label = QLabel("-")
        self.source_label = QLabel("-")
        self.destination_label = QLabel("-")
        self.status_mission_label = QLabel("-")
        
        mission_details_layout.addRow("Mission ID:", self.mission_id_label)
        mission_details_layout.addRow("Truck ID:", self.truck_id_label)
        mission_details_layout.addRow("Status:", self.status_mission_label)
        mission_details_layout.addRow("From:", self.source_label)
        mission_details_layout.addRow("To:", self.destination_label)
        
        card_info_layout.addLayout(mission_details_layout)
        
        # Driver information
        driver_group = QGroupBox("Driver Information")
        driver_layout = QFormLayout()
        
        self.driver_name_label = QLabel("-")
        self.driver_license_label = QLabel("-")
        
        driver_layout.addRow("Name:", self.driver_name_label)
        driver_layout.addRow("License:", self.driver_license_label)
        
        # Driver photo
        self.driver_photo_label = QLabel("No photo")
        self.driver_photo_label.setAlignment(Qt.AlignCenter)
        self.driver_photo_label.setMinimumHeight(150)
        self.driver_photo_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        driver_layout.addRow("Photo:", self.driver_photo_label)
        
        driver_group.setLayout(driver_layout)
        card_info_layout.addWidget(driver_group)
        
        # Articles table
        articles_label = QLabel("Articles")
        articles_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        card_info_layout.addWidget(articles_label)
        
        self.articles_table = QTableWidget()
        self.articles_table.setColumnCount(2)
        self.articles_table.setHorizontalHeaderLabels(["Article Code", "Quantity"])
        self.articles_table.horizontalHeader().setStretchLastSection(True)
        self.articles_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        card_info_layout.addWidget(self.articles_table)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.approve_btn = QPushButton("✓ Approve Delivery")
        self.approve_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.approve_btn.clicked.connect(self.on_approve_delivery)
        
        self.reject_btn = QPushButton("✗ Reject")
        self.reject_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        self.reject_btn.clicked.connect(self.on_reject_delivery)
        
        buttons_layout.addWidget(self.approve_btn)
        buttons_layout.addWidget(self.reject_btn)
        
        card_info_layout.addLayout(buttons_layout)
        
        self.card_info_box.setLayout(card_info_layout)
        main_layout.addWidget(self.card_info_box)
        
    def load_expected_missions(self):
        """Load expected missions into the table"""
        # Filter missions for this destination
        filtered_missions = [
            m for m in self.expected_missions 
            if m.get('destination') == self.destination_point
        ]
        
        self.missions_table.setRowCount(len(filtered_missions))
        
        for row, mission in enumerate(filtered_missions):
            self.missions_table.setItem(row, 0, QTableWidgetItem(mission.get('mission_id', '-')))
            self.missions_table.setItem(row, 1, QTableWidgetItem(mission.get('truck_id', '-')))
            self.missions_table.setItem(row, 2, QTableWidgetItem(mission.get('source', '-')))
        
        print(f"Loaded {len(filtered_missions)} missions for {self.destination_point}")
        
    def on_read_card(self):
        """Handle card reading - to be connected to actual card reader"""
        # TODO: Connect to actual card reading logic
        # For now, this is a placeholder that will be connected externally
        self.status_label.setText("Reading card...")
        self.status_label.setStyleSheet("padding: 10px; font-size: 12px; color: blue;")
        
        # Emit signal or call external function
        # The main application should connect this to the card reader
        print("Card read initiated - waiting for card data...")
        
    def validate_and_display_card(self, card_data):
        """
        Validate card data against expected missions and display results
        
        card_data format:
        {
            'mission': {'mission_id': ..., 'truck_id': ..., 'status': ..., 'source': ..., 'destination': ...},
            'driver': {'name': ..., 'license': ..., 'photo_data': ..., 'photo_meta': ...},
            'articles': [{'code': ..., 'quantity': ...}, ...]
        }
        """
        mission_id = card_data['mission']['mission_id']
        
        # Check if mission is expected
        mission_found = None
        for mission in self.expected_missions:
            if (mission.get('mission_id') == mission_id and 
                mission.get('destination') == self.destination_point):
                mission_found = mission
                break
        
        if not mission_found:
            # Mission not found or wrong destination
            QMessageBox.critical(
                self,
                "Invalid Card",
                f"Mission {mission_id} is not expected at this destination!\n\n"
                f"Expected destination: {self.destination_point}\n"
                f"Card destination: {card_data['mission']['destination']}"
            )
            self.status_label.setText("❌ INVALID CARD")
            self.status_label.setStyleSheet("padding: 10px; font-size: 14px; color: red; font-weight: bold;")
            self.card_info_box.setVisible(False)
            return
        
        # Valid mission - display data
        self.missions_box.setVisible(False)
        self.card_section.setVisible(False)       

        self.current_card_data = card_data
        self.display_card_info(card_data)
        
        self.status_label.setText("✅ VALID MISSION")
        self.status_label.setStyleSheet("padding: 10px; font-size: 14px; color: green; font-weight: bold;")
        
    def display_card_info(self, card_data):
        """Display card information in the interface"""
        # Show the card info box
        self.card_info_box.setVisible(True)
        
        # Mission details
        mission = card_data['mission']
        self.mission_id_label.setText(mission['mission_id'])
        self.truck_id_label.setText(mission['truck_id'])
        self.status_mission_label.setText(mission['status'])
        self.source_label.setText(mission['source'])
        self.destination_label.setText(mission['destination'])
        
        # Driver details
        driver = card_data['driver']
        self.driver_name_label.setText(driver['name'])
        self.driver_license_label.setText(driver.get('license', '-'))
        
        # Driver photo
        if 'photo_data' in driver and driver['photo_data']:
            try:
                # Decompress and display photo
                image = self.image_processor.decompress(
                    driver['photo_data'],
                    driver['photo_meta']
                )
                pixmap = QPixmap.fromImage(image)
                scaled_pixmap = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.driver_photo_label.setPixmap(scaled_pixmap)
                self.driver_photo_label.setText("")
            except Exception as e:
                self.driver_photo_label.setText(f"Error loading photo: {str(e)}")
        
        # Articles
        articles = card_data['articles']
        self.articles_table.setRowCount(len(articles))
        
        for row, article in enumerate(articles):
            self.articles_table.setItem(row, 0, QTableWidgetItem(article['code']))
            self.articles_table.setItem(row, 1, QTableWidgetItem(str(article['quantity'])))
        
    def on_approve_delivery(self):
        """Handle delivery approval"""
        if not self.current_card_data:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Approval",
            "Approve this delivery and mark as DELIVERED?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: Update mission status to DELIVERED on card
            # TODO: Update database
            
            self.card_validated.emit({
                'action': 'approved',
                'data': self.current_card_data
            })
            
            QMessageBox.information(self, "Success", "Delivery approved!")
            self.reset_interface()
        
    def on_reject_delivery(self):
        """Handle delivery rejection"""
        if not self.current_card_data:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Rejection",
            "Reject this delivery?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.card_validated.emit({
                'action': 'rejected',
                'data': self.current_card_data
            })
            
            QMessageBox.warning(self, "Rejected", "Delivery rejected!")
            self.reset_interface()
        
    def reset_interface(self):
        """Reset interface to initial state"""
        self.card_info_box.setVisible(False)
        self.current_card_data = None
        self.status_label.setText("Waiting for card...")
        self.status_label.setStyleSheet("padding: 10px; font-size: 12px;")

        self.missions_box.setVisible(True)
        self.card_section.setVisible(True)        
    def on_back_clicked(self):
        """Emit signal to go back to main interface"""
        self.back_clicked.emit()
        
    def set_expected_missions(self, missions_list):
        """Update expected missions from external source"""
        self.expected_missions = missions_list
        self.load_expected_missions()
        
    def set_destination_point(self, destination):
        """Update the destination point"""
        self.destination_point = destination
        self.load_expected_missions()
