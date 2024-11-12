from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QListWidget, QListWidgetItem,
                             QInputDialog, QMessageBox)
from PySide6.QtCore import Signal, Qt

from managers.categories_rule_dialog import CategoryRulesDialog
import os

class TileCategoryManager(QWidget):
    categoryChanged = Signal(dict)  # Emits when categories are modified

    def __init__(self):
        super().__init__()
        self.categories = {}  # Format: {category_name: set(tile_indices)}
        self.selected_tile_indices = []  # Store currently selected tiles
        self.rules_dir = "rules"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Tile Categories")
        header_label.setStyleSheet("color: #CCCCCC; font-weight: bold;")
        add_button = QPushButton("Add Category")
        add_button.clicked.connect(self.add_category)
        header_layout.addWidget(header_label)
        header_layout.addWidget(add_button)
        layout.addLayout(header_layout)

        # Categories list
        self.categories_list = QListWidget()
        self.categories_list.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                border: 1px solid #454545;
                color: #CCCCCC;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2D2D2D;
            }
            QListWidget::item:selected {
                background-color: #264F78;
            }
            QListWidget::item:hover {
                background-color: #2D2D2D;
            }
        """)
        layout.addWidget(self.categories_list)

        # Selected tiles display
        self.tiles_label = QLabel("Selected Tiles: None")
        self.tiles_label.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(self.tiles_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.assign_button = QPushButton("Assign Selected Tiles")
        self.edit_rules_button = QPushButton("Edit Rules")
        remove_button = QPushButton("Remove Category")

        self.assign_button.clicked.connect(self.assign_tiles)
        self.edit_rules_button.clicked.connect(self.edit_category_rules)
        remove_button.clicked.connect(self.remove_category)

        buttons_layout.addWidget(self.assign_button)
        buttons_layout.addWidget(self.edit_rules_button)
        buttons_layout.addWidget(remove_button)

        # Update button states
        self.edit_rules_button.setEnabled(False)
        self.categories_list.itemSelectionChanged.connect(self.update_button_states)

        layout.addLayout(buttons_layout)

    def add_category(self):
        name, ok = QInputDialog.getText(self, "New Category",
                                      "Enter category name:",
                                      QLineEdit.Normal)
        if ok and name:
            if name not in self.categories:
                self.categories[name] = set()
                self.update_categories_list()
                self.categoryChanged.emit(self.get_categories_dict())
            else:
                QMessageBox.warning(self, "Warning",
                                  "Category already exists!")

    def remove_category(self):
        current_item = self.categories_list.currentItem()
        if current_item:
            category_name = current_item.text().split(" [")[0]

            self.delete_category_rules(category_name)

            del self.categories[category_name]
            self.update_categories_list()
            self.categoryChanged.emit(self.get_categories_dict())

    def assign_tiles(self):  # Modified to use stored tile indices
        current_item = self.categories_list.currentItem()
        if current_item and self.selected_tile_indices:
            category_name = current_item.text().split(" [")[0]
            self.categories[category_name].update(self.selected_tile_indices)
            self.update_categories_list()
            self.categoryChanged.emit(self.get_categories_dict())
        elif not current_item:
            QMessageBox.warning(self, "Warning", "Please select a category first!")
        elif not self.selected_tile_indices:
            QMessageBox.warning(self, "Warning", "Please select tiles first!")

    def update_categories_list(self):
        self.categories_list.clear()
        for name, tiles in self.categories.items():
            item_text = f"{name} [{len(tiles)} tiles]"
            item = QListWidgetItem(item_text)
            self.categories_list.addItem(item)

    def get_categories_dict(self):
        return {name: list(tiles) for name, tiles in self.categories.items()}

    def set_selected_tiles(self, tile_indices):
        """Update the display of currently selected tiles and store them"""
        self.selected_tile_indices = tile_indices  # Store the selected tiles
        if tile_indices:
            self.tiles_label.setText(f"Selected Tiles: {tile_indices}")
        else:
            self.tiles_label.setText("Selected Tiles: None")

    def update_button_states(self):
        """Enable/disable buttons based on selection"""
        has_selection = self.categories_list.currentItem() is not None
        self.edit_rules_button.setEnabled(has_selection)

    def edit_category_rules(self):
        current_item = self.categories_list.currentItem()
        if current_item:
            category_name = current_item.text().split(" [")[0]
            dialog = CategoryRulesDialog(category_name, self)
            dialog.exec()

    def delete_category_rules(self, category_name):
        """Elimina todos los archivos asociados a la categoria correspondiente"""
        if os.path.exists(self.rules_dir):
            for filename in os.listdir(self.rules_dir):
                if filename.startswith(f"{category_name}_") and filename.endswith(".json"):
                    try:
                        file_path = os.path.join(self.rules_dir, filename)
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error al intentar borrar el archivo {filename}: {str(e)}")