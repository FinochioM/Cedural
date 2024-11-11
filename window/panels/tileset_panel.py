from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QFileDialog, QSizePolicy, QScrollArea, QHBoxLayout)
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PySide6.QtCore import Qt, QRect, Signal
from PIL import Image
import io
from .base_panel import BasePanel


class TilePreview(QLabel):
    """Widget to display the currently selected tile"""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(84, 84)  # Increased size according to wireframe
        self.setMaximumSize(84, 84)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #1E1E1E;
                border: 1px dashed #454545;
            }
        """)
        self.setText("No tile selected")

    def setTile(self, pixmap):
        if pixmap:
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        else:
            self.setText("No tile selected")


class TilesetViewer(QLabel):
    """Custom widget for displaying tileset with grid and selection"""
    tileSelected = Signal(int, int)  # Emits row, col of selected tile

    def __init__(self):
        super().__init__()
        self.tile_width = 32
        self.tile_height = 32
        self.tile_spacing = 0
        self.selected_tile = None
        self.setMouseTracking(True)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def setTileSize(self, width, height, spacing):
        self.tile_width = width
        self.tile_height = height
        self.tile_spacing = spacing
        if self.pixmap():
            self.adjustSize()
            self.updateGrid()

    def updateGrid(self):
        if self.pixmap():
            self.drawGrid()

    def setPixmap(self, pixmap):
        super().setPixmap(pixmap)
        if pixmap:
            self.adjustSize()

    def adjustSize(self):
        if self.pixmap():
            # Calculate the number of complete tiles that fit in the image
            num_cols = self.pixmap().width() // (self.tile_width + self.tile_spacing)
            num_rows = self.pixmap().height() // (self.tile_height + self.tile_spacing)

            # Set the size to exactly fit the complete tiles
            width = num_cols * (self.tile_width + self.tile_spacing)
            height = num_rows * (self.tile_height + self.tile_spacing)

            # Create a new pixmap of the exact size needed
            new_pixmap = self.pixmap().copy(0, 0, width, height)
            super().setPixmap(new_pixmap)
            self.setFixedSize(width, height)

    def drawGrid(self):
        if not self.pixmap():
            return

        grid_pixmap = QPixmap(self.pixmap())
        painter = QPainter(grid_pixmap)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Draw grid
        pen = QPen(QColor("#454545"))
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw vertical lines
        for x in range(0, grid_pixmap.width(), self.tile_width + self.tile_spacing):
            painter.drawLine(x, 0, x, grid_pixmap.height())

        # Draw horizontal lines
        for y in range(0, grid_pixmap.height(), self.tile_height + self.tile_spacing):
            painter.drawLine(0, y, grid_pixmap.width(), y)

        # Highlight selected tile if any
        if self.selected_tile:
            row, col = self.selected_tile
            x = col * (self.tile_width + self.tile_spacing)
            y = row * (self.tile_height + self.tile_spacing)
            highlight_pen = QPen(QColor("#264F78"))
            highlight_pen.setWidth(2)
            painter.setPen(highlight_pen)
            painter.drawRect(x, y, self.tile_width, self.tile_height)

        painter.end()
        self.setPixmap(grid_pixmap)

    def mousePressEvent(self, event):
        if not self.pixmap() or event.button() != Qt.LeftButton:
            return

        pos = event.pos()
        col = pos.x() // (self.tile_width + self.tile_spacing)
        row = pos.y() // (self.tile_height + self.tile_spacing)

        max_col = (self.pixmap().width() // (self.tile_width + self.tile_spacing)) - 1
        max_row = (self.pixmap().height() // (self.tile_height + self.tile_spacing)) - 1

        if 0 <= col <= max_col and 0 <= row <= max_row:
            self.selected_tile = (row, col)
            self.drawGrid()
            self.tileSelected.emit(row, col)


class TilesetPanel(BasePanel):
    def __init__(self, settings_panel=None):
        super().__init__("Tileset")
        self.settings_panel = settings_panel
        self.current_tileset = None
        self.init_panel()

    def init_panel(self):
        # Load button with specific height and style
        load_button = QPushButton("Load Tileset")
        load_button.setMinimumHeight(30)
        load_button.setStyleSheet("""
            QPushButton {
                background-color: #264F78;
                border: none;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #365F88;
            }
        """)
        load_button.clicked.connect(self.load_tileset)
        self.content_layout.addWidget(load_button)

        # Container for tile preview
        preview_container = QWidget()
        preview_container.setFixedHeight(100)
        preview_container.setStyleSheet("""
            background-color: #1E1E1E;
            border: 1px solid #454545;
        """)
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)
        preview_layout.setAlignment(Qt.AlignCenter)

        # Selected tile preview
        self.tile_preview = TilePreview()
        preview_layout.addWidget(self.tile_preview, alignment=Qt.AlignCenter)
        self.content_layout.addWidget(preview_container)

        # Tileset viewer container
        viewer_container = QWidget()
        viewer_container.setStyleSheet("""
            background-color: #1E1E1E;
            border: 1px solid #454545;
        """)
        viewer_layout = QVBoxLayout(viewer_container)
        viewer_layout.setContentsMargins(5, 5, 5, 5)
        viewer_layout.setSpacing(0)

        # Scroll area for tileset
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar {
                background-color: #1E1E1E;
            }
            QScrollBar:vertical {
                width: 12px;
            }
            QScrollBar:horizontal {
                height: 12px;
            }
        """)

        # Centering container for the tileset viewer
        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setAlignment(Qt.AlignCenter)

        # Tileset viewer widget
        self.tileset_viewer = TilesetViewer()
        self.tileset_viewer.tileSelected.connect(self.on_tile_selected)
        center_layout.addWidget(self.tileset_viewer)

        scroll_area.setWidget(center_container)
        viewer_layout.addWidget(scroll_area)
        self.content_layout.addWidget(viewer_container)

        # Add stretching space at the bottom
        self.content_layout.addStretch()

    def load_tileset(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Load Tileset",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )

        if file_name:
            try:
                image = Image.open(file_name)
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                buffer.seek(0)

                self.current_tileset = image

                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())

                if self.settings_panel:
                    self.tileset_viewer.setTileSize(
                        self.settings_panel.tile_width_spin.value(),
                        self.settings_panel.tile_height_spin.value(),
                        self.settings_panel.tile_spacing_spin.value()
                    )

                self.tileset_viewer.setPixmap(pixmap)
                self.tileset_viewer.updateGrid()

            except Exception as e:
                self.tileset_viewer.setText(f"Error loading tileset: {str(e)}")
                self.current_tileset = None

    def on_tile_selected(self, row, col):
        if not self.current_tileset:
            return

        x = col * (self.tileset_viewer.tile_width + self.tileset_viewer.tile_spacing)
        y = row * (self.tileset_viewer.tile_height + self.tileset_viewer.tile_spacing)

        full_pixmap = self.tileset_viewer.pixmap()
        tile_pixmap = full_pixmap.copy(
            QRect(x, y, self.tileset_viewer.tile_width, self.tileset_viewer.tile_height)
        )

        self.tile_preview.setTile(tile_pixmap)