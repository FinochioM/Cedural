from PySide6.QtWidgets import (QVBoxLayout, QLabel, QPushButton,
                               QSpinBox, QGroupBox, QHBoxLayout)

from managers.rules_managers.tile_category_manager import TileCategoryManager
from .base_panel import BasePanel


class SettingsPanel(BasePanel):
    def __init__(self):
        super().__init__("Generation Settings")
        self.init_panel()

    def init_panel(self):
        # Tile settings Controls
        tile_settings_group = self.create_tile_settings()
        self.content_layout.addWidget(tile_settings_group)

        # Room Size Controls
        size_group = self.create_size_controls()
        self.content_layout.addWidget(size_group)

        # Rules Section with Category Manager
        rules_group = self.create_rules_section()
        self.content_layout.addWidget(rules_group)

        # Control Buttons
        buttons_group = self.create_control_buttons()
        self.content_layout.addWidget(buttons_group)

        # Add stretching space
        self.content_layout.addStretch()

    def create_size_controls(self):
        group = QGroupBox("Room Size")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #454545;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #CCCCCC;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
            }
        """)

        layout = QVBoxLayout()

        # Width control
        width_layout = QHBoxLayout()
        width_label = QLabel("Width:")
        width_label.setStyleSheet("color: #CCCCCC;")
        width_spin = QSpinBox()
        width_spin.setRange(5, 100)
        width_spin.setValue(20)
        width_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #454545;
                padding: 2px;
            }
        """)
        width_layout.addWidget(width_label)
        width_layout.addWidget(width_spin)

        # Height control
        height_layout = QHBoxLayout()
        height_label = QLabel("Height:")
        height_label.setStyleSheet("color: #CCCCCC;")
        height_spin = QSpinBox()
        height_spin.setRange(5, 100)
        height_spin.setValue(15)
        height_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #454545;
                padding: 2px;
            }
        """)
        height_layout.addWidget(height_label)
        height_layout.addWidget(height_spin)

        layout.addLayout(width_layout)
        layout.addLayout(height_layout)
        group.setLayout(layout)

        return group

    def create_rules_section(self):
        group = QGroupBox("Rules")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #454545;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #CCCCCC;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
            }
        """)

        layout = QVBoxLayout()

        # Add only the category manager
        self.category_manager = TileCategoryManager()
        layout.addWidget(self.category_manager)

        group.setLayout(layout)
        return group

    def create_control_buttons(self):
        group = QGroupBox("Controls")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #454545;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #CCCCCC;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
            }
        """)

        layout = QVBoxLayout()

        # Generate button
        generate_btn = QPushButton("Generate")
        generate_btn.setObjectName("generateButton")
        generate_btn.setMinimumHeight(30)

        # Save Configuration button
        save_btn = QPushButton("Save Configuration")
        save_btn.setMinimumHeight(30)

        # Load Configuration button
        load_btn = QPushButton("Load Configuration")
        load_btn.setMinimumHeight(30)

        layout.addWidget(generate_btn)
        layout.addWidget(save_btn)
        layout.addWidget(load_btn)

        group.setLayout(layout)
        return group

    def create_tile_settings(self):
        group = QGroupBox("Tile Settings")
        group.setStyleSheet("""
                    QGroupBox {
                border: 1px solid #454545;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #CCCCCC;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
            }
        """)

        layout = QVBoxLayout()

        tile_width_layout = QHBoxLayout()
        tile_width_label = QLabel("Tile Width:")
        tile_width_label.setStyleSheet("color: #CCCCCC;")
        self.tile_width_spin = QSpinBox()
        self.tile_width_spin.setRange(8, 128)
        self.tile_width_spin.setValue(32)
        self.tile_width_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #454545;
                padding: 2px;
            }
        """)

        tile_width_layout.addWidget(tile_width_label)
        tile_width_layout.addWidget(self.tile_width_spin)

        # Tile Height
        tile_height_layout = QHBoxLayout()
        tile_height_label = QLabel("Tile Height:")
        tile_height_label.setStyleSheet("color: #CCCCCC;")
        self.tile_height_spin = QSpinBox()
        self.tile_height_spin.setRange(8, 128)
        self.tile_height_spin.setValue(32)
        self.tile_height_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #454545;
                padding: 2px;
            }
        """)

        tile_height_layout.addWidget(tile_height_label)
        tile_height_layout.addWidget(self.tile_height_spin)

        # Tile Spacing
        tile_spacing_layout = QHBoxLayout()
        tile_spacing_label = QLabel("Tile Spacing:")
        tile_spacing_label.setStyleSheet("color: #CCCCCC;")
        self.tile_spacing_spin = QSpinBox()
        self.tile_spacing_spin.setRange(0, 16)
        self.tile_spacing_spin.setValue(0)
        self.tile_spacing_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #454545;
                padding: 2px;
            }
        """)
        tile_spacing_layout.addWidget(tile_spacing_label)
        tile_spacing_layout.addWidget(self.tile_spacing_spin)

        layout.addLayout(tile_width_layout)
        layout.addLayout(tile_height_layout)
        layout.addLayout(tile_spacing_layout)
        group.setLayout(layout)

        return group

    def on_categories_changed(self, categories_dict):
        """Update rules_managers editor when categories change"""
        self.rules_editor.update_category_list(categories_dict.keys())

    def on_category_selected(self, current, previous):
        """Load rules_managers for the selected category"""
        if current:
            category_name = current.text().split(" [")[0]
            self.rules_editor.load_category_rules(category_name)
    def update_tile_selection(self, selected_tiles):
        """Actualiza la selección de tiles en el category manager"""
        if hasattr(self, 'category_manager'):
            self.category_manager.set_selected_tiles(selected_tiles)

    def update_for_project_type(self, project_type):
        """Actualiza la UI según el tipo de proyecto"""
        # Actualizar configuraciones específicas del tipo de proyecto
        pass

    def update_grid_settings(self, grid_settings):
        """Actualiza configuraciones de grid"""
        if hasattr(self, 'tile_width_spin'):
            self.tile_width_spin.setValue(grid_settings.width)
            self.tile_height_spin.setValue(grid_settings.height)

    def update_for_workspace(self, workspace):
        """Actualiza configuraciones según el workspace"""
        pass

    def load_room_settings(self, room):
        """Carga configuraciones de una room"""
        pass