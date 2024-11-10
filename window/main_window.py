from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QSplitter
from PySide6.QtCore import Qt
from .panels.tileset_panel import TilesetPanel
from .panels.preview_panel import PreviewPanel
from .panels.settings_panel import SettingsPanel
from .menu.main_menu import MainMenu

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cedural - Tilemaps Generator")
        self.setMinimumSize(1280, 720)

        self.menu_bar = MainMenu(self)
        self.setMenuBar(self.menu_bar)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)

        # Crear los paneles principales
        self.tileset_panel = TilesetPanel()
        self.preview_panel = PreviewPanel()
        self.settings_panel = SettingsPanel()

        # Agregar paneles al splitter
        splitter.addWidget(self.tileset_panel)
        splitter.addWidget(self.preview_panel)
        splitter.addWidget(self.settings_panel)

        # Establecer tamaños iniciales de los paneles
        splitter.setSizes([240, 480, 240])

        # Agregar splitter al layout principal
        main_layout.addWidget(splitter)