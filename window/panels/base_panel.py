from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class BasePanel(QWidget):
    def __init__(self, title):
        super().__init__()
        self.init_ui(title)

    def init_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(30)
        header.setStyleSheet("background-color: #2D2D2D;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #CCCCCC; font-weight: bold;")
        header_layout.addWidget(title_label)

        layout.addWidget(header)

        # Content
        self.content = QWidget()
        self.content.setStyleSheet("background-color: #252526;")
        self.content_layout = QVBoxLayout(self.content)
        # Removemos el margen inferior del content_layout
        self.content_layout.setContentsMargins(10, 10, 10, 0)
        self.content_layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.content)