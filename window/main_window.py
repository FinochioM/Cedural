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

        # Create panels with proper connections
        self.settings_panel = SettingsPanel()
        self.tileset_panel = TilesetPanel(self.settings_panel)
        self.preview_panel = PreviewPanel()

        # Connect settings panel signals to tileset viewer
        self.settings_panel.tile_width_spin.valueChanged.connect(
            lambda v: self.update_tileset_grid()
        )
        self.settings_panel.tile_height_spin.valueChanged.connect(
            lambda v: self.update_tileset_grid()
        )
        self.settings_panel.tile_spacing_spin.valueChanged.connect(
            lambda v: self.update_tileset_grid()
        )

        # Add panels to splitter
        splitter.addWidget(self.tileset_panel)
        splitter.addWidget(self.preview_panel)
        splitter.addWidget(self.settings_panel)

        # Set initial sizes of panels
        splitter.setSizes([240, 480, 240])

        # Add splitter to main layout
        main_layout.addWidget(splitter)

    def update_tileset_grid(self):
        """Update the tileset grid when settings change"""
        if hasattr(self, 'tileset_panel') and hasattr(self.tileset_panel, 'tileset_viewer'):
            self.tileset_panel.tileset_viewer.setTileSize(
                self.settings_panel.tile_width_spin.value(),
                self.settings_panel.tile_height_spin.value(),
                self.settings_panel.tile_spacing_spin.value()
            )