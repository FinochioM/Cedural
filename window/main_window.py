from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QSplitter, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
from .panels.tileset_panel import TilesetPanel
from .panels.preview_panel import PreviewPanel
from .panels.settings_panel import SettingsPanel
from .menu.main_menu import MainMenu
from .panels.workspace_panel import WorkspacePanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cedural - Tilemaps Generator")
        self.setMinimumSize(1280, 720)

        self.menu_bar = MainMenu(self)
        self.setMenuBar(self.menu_bar)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Left container with vertical splitter
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Vertical splitter for tileset and workspace panels
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #353535;
                height: 2px;
            }
            QSplitter::handle:hover {
                background-color: #454545;
            }
        """)

        # Create panels
        self.settings_panel = SettingsPanel()
        self.tileset_panel = TilesetPanel(self.settings_panel)
        self.preview_panel = PreviewPanel()
        self.workspace_panel = WorkspacePanel()

        # Add panels to vertical splitter
        vertical_splitter.addWidget(self.tileset_panel)
        vertical_splitter.addWidget(self.workspace_panel)

        # Set initial sizes for vertical splitter (maintain proportions from wireframe)
        vertical_splitter.setSizes([580, 190])  # Aproximadamente la proporción original

        # Add vertical splitter to left layout
        left_layout.addWidget(vertical_splitter)

        # Connect settings panel signals
        self.settings_panel.tile_width_spin.valueChanged.connect(self.update_tileset_grid)
        self.settings_panel.tile_height_spin.valueChanged.connect(self.update_tileset_grid)
        self.settings_panel.tile_spacing_spin.valueChanged.connect(self.update_tileset_grid)
        self.tileset_panel.tilesSelected.connect(self.settings_panel.category_manager.set_selected_tiles)

        # Add to main splitter
        main_splitter.addWidget(left_container)
        main_splitter.addWidget(self.preview_panel)
        main_splitter.addWidget(self.settings_panel)

        # Set initial sizes for main splitter
        main_splitter.setSizes([300, 600, 300])

        # Add to main layout
        main_layout.addWidget(main_splitter)

    def update_tileset_grid(self):
        if hasattr(self, 'tileset_panel') and hasattr(self.tileset_panel, 'tileset_viewer'):
            self.tileset_panel.tileset_viewer.setTileSize(
                self.settings_panel.tile_width_spin.value(),
                self.settings_panel.tile_height_spin.value(),
                self.settings_panel.tile_spacing_spin.value()
            )