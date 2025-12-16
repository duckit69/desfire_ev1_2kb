# source_interface.py


from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QGroupBox, QFormLayout, 
                             QTableWidget, QTableWidgetItem, QFileDialog, 
                             QComboBox, QCompleter)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from .pic_codec import CardImageCodec, HashManager

class SourceInterface(QWidget):
    # Signal to go back to main interface
    back_clicked = pyqtSignal()
    form_submitted = pyqtSignal(dict)


    def __init__(self, articles_list=None, trucks_list=None):
        super().__init__()
        self.image_path = None
        self.image_processor = CardImageCodec()
        
        # Articles database - store full objects
        self.articles_database = articles_list if articles_list else []
        
        # Trucks database - store full objects
        self.trucks_database = trucks_list if trucks_list else []
        
        # Create lookup dictionaries for easy access
        self.articles_by_content = {item['content']: item for item in self.articles_database}
        self.trucks_by_display = {}
        
        self.hashManager = HashManager()
        
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Back button at the top
        back_btn = QPushButton("← Back")
        back_btn.setMaximumWidth(100)
        back_btn.clicked.connect(self.on_back_clicked)
        main_layout.addWidget(back_btn)
        
        # === Box 1: Driver Information ===
        driver_box = QGroupBox("Driver Information")
        driver_layout = QFormLayout()
        
        # Driver Name
        self.driver_name_input = QLineEdit()
        self.driver_name_input.setPlaceholderText("Enter driver name")
        driver_layout.addRow("Name:", self.driver_name_input)
        
        # Driver License
        self.driver_license_input = QLineEdit()
        self.driver_license_input.setPlaceholderText("Enter license number")
        driver_layout.addRow("License:", self.driver_license_input)
        
        # Image upload section
        image_layout = QHBoxLayout()
        self.upload_image_btn = QPushButton("Upload Image")
        self.upload_image_btn.clicked.connect(self.upload_image)
        image_layout.addWidget(self.upload_image_btn)
        
        self.image_label = QLabel("No image uploaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(100)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        
        driver_layout.addRow("Image:", image_layout)
        driver_layout.addRow("", self.image_label)
        
        driver_box.setLayout(driver_layout)
        main_layout.addWidget(driver_box)
        
        # === Box 2: Mission Information ===
        mission_box = QGroupBox("Mission Information")
        mission_layout = QFormLayout()
        
        # Status dropdown
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "In Progress", "Completed"])
        mission_layout.addRow("Status:", self.status_combo)
        
        # Truck Selection dropdown
        self.truck_combo = QComboBox()
        self.truck_combo.addItem("-- Select Truck --", None)  # Store None for default

        free_trucks = [truck for truck in self.trucks_database if truck.get('available') == 'Free']
        
        # Populate trucks with formatted display
        for truck in free_trucks:
            display_text = f"{truck['model']} - {truck['license_plate']}"
            self.truck_combo.addItem(display_text, truck)  # Store truck dict as data
            self.trucks_by_display[display_text] = truck
        
        mission_layout.addRow("Truck:", self.truck_combo)
        
        # Source
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Enter source location")
        mission_layout.addRow("Source:", self.source_input)
        
        # Destination
        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Enter destination location")
        mission_layout.addRow("Destination:", self.destination_input)
        
        mission_box.setLayout(mission_layout)
        main_layout.addWidget(mission_box)
        
        # === Article Search Section ===
        search_box = QGroupBox("Add Article")
        search_layout = QHBoxLayout()
        
        # Search input with autocomplete
        self.article_search_input = QLineEdit()
        self.article_search_input.setPlaceholderText("Search and select article...")
        
        # Setup autocomplete with article names only
        article_names = [item['content'] for item in self.articles_database]
        completer = QCompleter(article_names)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.article_search_input.setCompleter(completer)
        
        # Add button
        add_article_btn = QPushButton("Add to Table")
        add_article_btn.clicked.connect(self.add_article_to_table)
        
        search_layout.addWidget(self.article_search_input)
        search_layout.addWidget(add_article_btn)
        search_box.setLayout(search_layout)
        main_layout.addWidget(search_box)
        
        # === Table: Articles and Quantities ===
        table_label = QLabel("Articles")
        table_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        main_layout.addWidget(table_label)
        
        self.articles_table = QTableWidget()
        self.articles_table.setColumnCount(2)
        self.articles_table.setHorizontalHeaderLabels(["Article", "Quantity"])
        self.articles_table.setRowCount(0)  # Start with 0 rows
        self.articles_table.horizontalHeader().setStretchLastSection(True)
        
        # Make Article column read-only, Quantity editable
        self.articles_table.setColumnWidth(0, 300)
        
        main_layout.addWidget(self.articles_table)
        
        # Remove row button
        table_buttons_layout = QHBoxLayout()
        remove_row_btn = QPushButton("Remove Selected Row")
        remove_row_btn.clicked.connect(self.remove_selected_row)
        
        table_buttons_layout.addWidget(remove_row_btn)
        table_buttons_layout.addStretch()
        main_layout.addLayout(table_buttons_layout)
        
        # Submit button
        submit_btn = QPushButton("Submit")
        submit_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        submit_btn.clicked.connect(self.on_submit)
        main_layout.addWidget(submit_btn)
        
    def add_article_to_table(self):
        """Add selected article to table with default quantity of 1"""
        article_name = self.article_search_input.text().strip()
        
        # Check if article exists in database
        if article_name not in self.articles_by_content:
            print(f"Article '{article_name}' not found in database")
            return
            
        # Check if article already exists in table
        for row in range(self.articles_table.rowCount()):
            existing_article = self.articles_table.item(row, 0)
            if existing_article and existing_article.text() == article_name:
                print(f"Article '{article_name}' already in table")
                return
        
        # Add new row
        current_rows = self.articles_table.rowCount()
        self.articles_table.insertRow(current_rows)
        
        # Add article name (read-only)
        article_item = QTableWidgetItem(article_name)
        article_item.setFlags(article_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
        
        # Store the full article object as item data for later retrieval
        article_item.setData(Qt.UserRole, self.articles_by_content[article_name])
        
        self.articles_table.setItem(current_rows, 0, article_item)
        
        # Add default quantity (editable)
        quantity_item = QTableWidgetItem("1")
        self.articles_table.setItem(current_rows, 1, quantity_item)
        
        # Clear search input
        self.article_search_input.clear()
        
        print(f"Added: {article_name} with quantity 1")
        
    def remove_selected_row(self):
        """Remove the currently selected row"""
        current_row = self.articles_table.currentRow()
        if current_row >= 0:
            self.articles_table.removeRow(current_row)
            print(f"Removed row {current_row}")
        
    def upload_image(self):
        """Open file dialog to upload an image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Driver Image", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.image_path = file_path
            # Display the image
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setText("")  # Clear the "No image" text
            print(f"Image uploaded: {file_path}")
            
    def on_back_clicked(self):
        """Emit signal to go back to main interface"""
        self.back_clicked.emit()
        
    def on_submit(self):
        """Handle form submission"""
        # Collect all data
        driver_name = self.driver_name_input.text()
        driver_license = self.driver_license_input.text()
        status = self.status_combo.currentText()
        
        # Get selected truck (stored as item data)
        selected_truck = self.truck_combo.currentData()
        
        source = self.source_input.text()
        destination = self.destination_input.text()
        
        # Collect table data with full article objects
        articles = []
        for row in range(self.articles_table.rowCount()):
            article_item = self.articles_table.item(row, 0)
            quantity_item = self.articles_table.item(row, 1)
            
            if article_item and quantity_item:
                # Get the full article object stored in item data
                article_obj = article_item.data(Qt.UserRole)
                quantity = quantity_item.text()
                
                if article_obj and quantity:
                    # Add quantity to the article object
                    article_with_quantity = article_obj.copy()
                    article_with_quantity['quantity'] = quantity
                    articles.append(article_with_quantity)
        
        # Process image if it exists
        image_vector = None
        if self.image_path:
            total_size, data, meta = self.image_processor.usable_compress(self.image_path)
        
        hashed = self.hashManager.hash_list(articles)
        
        # Create form data dictionary
        form_data = {
            "driver_name": driver_name,
            "driver_license": driver_license,
            "image_vec": data,
            "image_metaData": meta,
            "mission_status": status,
            "truck": selected_truck,  # Full truck object or None
            "source": source,
            "destination": destination,
            "articles": articles,  # Full article objects with quantity
            "hashed_articles_table": hashed
        }
        
        print(f"Selected truck: {selected_truck}")
        print(f"Articles with full data: {articles}")
        self.form_submitted.emit(form_data)
    
    def set_articles_database(self, articles_list):
        """Update the articles database from external source"""
        self.articles_database = articles_list
        self.articles_by_content = {item['content']: item for item in self.articles_database}
        
        # Update autocomplete
        article_names = [item['content'] for item in self.articles_database]
        completer = QCompleter(article_names)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.article_search_input.setCompleter(completer)
    
    def set_trucks_database(self, trucks_list):
        """Update the trucks database from external source"""
        self.trucks_database = trucks_list
        self.trucks_by_display = {}
        
        # Clear and repopulate the truck dropdown
        self.truck_combo.clear()
        self.truck_combo.addItem("-- Select Truck --", None)
        
        # Filter only free trucks
        free_trucks = [truck for truck in self.trucks_database if truck.get('available') == 'Free']
        
        for truck in free_trucks:
            display_text = f"{truck['model']} - {truck['license_plate']}"
            self.truck_combo.addItem(display_text, truck)
            self.trucks_by_display[display_text] = truck
