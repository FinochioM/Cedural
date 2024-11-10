from PySide6.QtWidgets import QWidget
from window.panels.base_panel import BasePanel


class TilesetPanel(BasePanel):
    def __init__(self):
        super().__init__("Tileset")
        self.init_panel()

    def init_panel(self):
        # Área de previsualización del tileset
        tileset_preview = QWidget()
        tileset_preview.setMinimumHeight(220)
        tileset_preview.setStyleSheet("""
            background-color: #1E1E1E;
            border: 1px dashed #454545;
        """)
        self.content_layout.addWidget(tileset_preview)

        # Sección de categorías
        categories_header = QWidget()
        categories_header.setFixedHeight(30)
        categories_header.setStyleSheet("background-color: #2D2D2D;")
        self.content_layout.addWidget(categories_header)

        categories_content = QWidget()
        categories_content.setStyleSheet("""
            background-color: #1E1E1E;
            border: 1px solid #454545;
        """)
        self.content_layout.addWidget(categories_content)