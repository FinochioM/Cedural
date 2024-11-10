from PySide6.QtWidgets import QWidget
from .base_panel import BasePanel

class PreviewPanel(BasePanel):
    def __init__(self):
        super().__init__("Room Preview")
        self.init_panel()

    def init_panel(self):
        # Área de previsualización de la sala
        preview_area = QWidget()
        preview_area.setStyleSheet("""
            background-color: #1E1E1E;
            border: 1px dashed #454545;
        """)
        self.content_layout.addWidget(preview_area)