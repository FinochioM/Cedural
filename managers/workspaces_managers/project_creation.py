from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QComboBox, QSpinBox, QPushButton,
                               QFileDialog, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt


class ProjectCreationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Información básica
        basic_group = QGroupBox("Project Information")
        basic_layout = QVBoxLayout()

        # Nombre del proyecto
        name_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        name_layout.addWidget(QLabel("Project Name:"))
        name_layout.addWidget(self.name_input)
        basic_layout.addLayout(name_layout)

        # Tipo de proyecto
        type_layout = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Top-Down View", "Side Scroller"])
        type_layout.addWidget(QLabel("Project Type:"))
        type_layout.addWidget(self.type_combo)
        basic_layout.addLayout(type_layout)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # Configuración de Grid
        grid_group = QGroupBox("Grid Settings")
        grid_layout = QVBoxLayout()

        # Tamaño de tile
        tile_layout = QHBoxLayout()
        self.tile_width = QSpinBox()
        self.tile_height = QSpinBox()
        self.tile_width.setRange(8, 128)
        self.tile_height.setRange(8, 128)
        self.tile_width.setValue(32)
        self.tile_height.setValue(32)

        tile_layout.addWidget(QLabel("Tile Width:"))
        tile_layout.addWidget(self.tile_width)
        tile_layout.addWidget(QLabel("Tile Height:"))
        tile_layout.addWidget(self.tile_height)
        grid_layout.addLayout(tile_layout)

        grid_group.setLayout(grid_layout)
        layout.addWidget(grid_group)

        # Default Room Settings
        room_group = QGroupBox("Default Room Settings")
        room_layout = QVBoxLayout()

        room_size_layout = QHBoxLayout()
        self.room_width = QSpinBox()
        self.room_height = QSpinBox()
        self.room_width.setRange(10, 100)
        self.room_height.setRange(10, 100)

        room_size_layout.addWidget(QLabel("Width (in tiles):"))
        room_size_layout.addWidget(self.room_width)
        room_size_layout.addWidget(QLabel("Height (in tiles):"))
        room_size_layout.addWidget(self.room_height)
        room_layout.addLayout(room_size_layout)

        room_group.setLayout(room_layout)
        layout.addWidget(room_group)

        # Botones
        button_layout = QHBoxLayout()
        create_button = QPushButton("Create Project")
        cancel_button = QPushButton("Cancel")

        create_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(create_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Conectar cambios de tipo de proyecto
        self.type_combo.currentIndexChanged.connect(self.update_defaults)
        self.update_defaults(0)

        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
                color: #CCCCCC;
            }
            QGroupBox {
                border: 1px solid #454545;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #CCCCCC;
            }
            QLabel {
                color: #CCCCCC;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #454545;
                padding: 5px;
            }
            QPushButton {
                background-color: #264F78;
                color: white;
                border: none;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #365F88;
            }
        """)

    def update_defaults(self, index):
        """Actualiza valores por defecto según el tipo de proyecto"""
        if self.type_combo.currentText() == "Top-Down View":
            self.room_width.setValue(20)
            self.room_height.setValue(15)
        else:  # Side Scroller
            self.room_width.setValue(30)
            self.room_height.setValue(20)

    def get_project_data(self) -> dict:
        """Recopila todos los datos del proyecto"""
        return {
            "name": self.name_input.text(),
            "type": "topdown" if self.type_combo.currentText() == "Top-Down View" else "sidescroller",
            "grid": {
                "width": self.tile_width.value(),
                "height": self.tile_height.value()
            },
            "default_room": {
                "width": self.room_width.value(),
                "height": self.room_height.value()
            }
        }