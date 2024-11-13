from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene,
                               QLabel, QPushButton, QHBoxLayout, QGraphicsRectItem)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QColor, QBrush, QPainter
from .base_panel import BasePanel
from managers.workspaces_managers.project_management import ProjectType, Room


class RoomPreviewScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.grid_size = 32
        self.room_width = 0
        self.room_height = 0
        self.project_type = ProjectType.TOPDOWN
        self.grid_color = QColor("#353535")
        self.background_color = QColor("#1E1E1E")

    def set_room_size(self, width: int, height: int):
        self.room_width = width * self.grid_size
        self.room_height = height * self.grid_size
        self.setSceneRect(0, 0, self.room_width, self.room_height)
        self.update()

    def set_project_type(self, project_type: ProjectType):
        self.project_type = project_type
        self.update()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        # Draw background
        painter.fillRect(rect, self.background_color)

        # Draw grid
        pen = QPen(self.grid_color)
        pen.setWidth(1)
        painter.setPen(pen)

        # Vertical lines
        for x in range(0, int(self.room_width) + 1, self.grid_size):
            painter.drawLine(x, 0, x, self.room_height)

        # Horizontal lines
        for y in range(0, int(self.room_height) + 1, self.grid_size):
            painter.drawLine(0, y, self.room_width, y)

        if self.project_type == ProjectType.SIDESCROLLER:
            # Dibujar indicadores de gravedad
            self.draw_gravity_indicators(painter)

    def draw_gravity_indicators(self, painter: QPainter):
        """Dibuja flechas que indican la dirección de la gravedad en side-scroller"""
        arrow_color = QColor("#666666")
        painter.setPen(QPen(arrow_color))
        painter.setBrush(QBrush(arrow_color))

        arrow_size = self.grid_size * 0.5
        margin = self.grid_size

        # Dibujar flechas en el borde derecho
        for y in range(margin, int(self.room_height - margin), int(self.grid_size * 3)):
            # Triángulo de la flecha
            points = [
                (self.room_width - margin, y),
                (self.room_width - margin - arrow_size, y - arrow_size / 2),
                (self.room_width - margin - arrow_size, y + arrow_size / 2)
            ]
            painter.drawPolygon(*[QPointF(x, y) for x, y in points])

            # Línea de la flecha
            painter.drawLine(
                self.room_width - margin - arrow_size,
                y,
                self.room_width - margin - arrow_size * 2,
                y
            )


class RoomPreviewView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))

        # Estilo para los scrollbars
        self.setStyleSheet("""
            QScrollBar:horizontal, QScrollBar:vertical {
                background: #1E1E1E;
                border: none;
            }
            QScrollBar::handle:horizontal, QScrollBar::handle:vertical {
                background: #454545;
                border-radius: 4px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::add-line:vertical,
            QScrollBar::sub-line:horizontal, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            # Zoom
            factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
            self.scale(factor, factor)
        else:
            # Scroll normal
            super().wheelEvent(event)


class PreviewPanel(BasePanel):
    def __init__(self):
        super().__init__("Room Preview")
        self.init_panel()
        self.current_room = None

    def init_panel(self):
        # Container principal
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Toolbar
        toolbar = QHBoxLayout()

        # Zoom controls
        zoom_in_btn = QPushButton("+")
        zoom_out_btn = QPushButton("-")
        reset_zoom_btn = QPushButton("Reset")

        for btn in [zoom_in_btn, zoom_out_btn, reset_zoom_btn]:
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #264F78;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #365F88;
                }
            """)
            toolbar.addWidget(btn)

        zoom_in_btn.clicked.connect(lambda: self.preview_view.scale(1.2, 1.2))
        zoom_out_btn.clicked.connect(lambda: self.preview_view.scale(1 / 1.2, 1 / 1.2))
        reset_zoom_btn.clicked.connect(self.reset_zoom)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Preview area
        self.preview_scene = RoomPreviewScene()
        self.preview_view = RoomPreviewView()
        self.preview_view.setScene(self.preview_scene)
        layout.addWidget(self.preview_view)

        # Info bar
        info_bar = QHBoxLayout()
        self.coordinates_label = QLabel("Pos: 0, 0")
        self.coordinates_label.setStyleSheet("color: #CCCCCC;")
        info_bar.addWidget(self.coordinates_label)
        info_bar.addStretch()

        self.room_size_label = QLabel("Size: 0x0")
        self.room_size_label.setStyleSheet("color: #CCCCCC;")
        info_bar.addWidget(self.room_size_label)

        layout.addLayout(info_bar)

        self.content_layout.addWidget(container)

    def reset_zoom(self):
        self.preview_view.resetTransform()
        # Ajustar la vista para mostrar toda la sala
        self.preview_view.fitInView(
            self.preview_scene.sceneRect(),
            Qt.KeepAspectRatio
        )

    def set_project_type(self, project_type: ProjectType):
        """Actualiza el tipo de proyecto y ajusta la visualización"""
        self.preview_scene.set_project_type(project_type)

    def load_room(self, room: Room):
        """Carga una sala para previsualización"""
        self.current_room = room
        self.preview_scene.set_room_size(room.width, room.height)
        self.room_size_label.setText(f"Size: {room.width}x{room.height}")
        # Limpiar la escena
        for item in self.preview_scene.items():
            self.preview_scene.removeItem(item)
        # Cargar tiles si existen
        if room.data:
            self.load_room_data(room.data)

    def load_room_data(self, data: list):
        """Carga los datos de tiles de la sala"""
        if not data or not self.current_room:
            return

        grid_size = self.preview_scene.grid_size
        for y, row in enumerate(data):
            for x, tile_id in enumerate(row):
                if tile_id > 0:  # 0 generalmente significa vacío
                    tile_item = self.create_tile_item(tile_id)
                    tile_item.setPos(x * grid_size, y * grid_size)
                    self.preview_scene.addItem(tile_item)

    def create_tile_item(self, tile_id: int):
        """Crea un item gráfico para representar un tile"""
        # Aquí deberías crear el item con la imagen del tile correcta
        # Por ahora solo crearemos un rectángulo coloreado
        rect = QGraphicsRectItem(0, 0, self.preview_scene.grid_size, self.preview_scene.grid_size)
        rect.setBrush(QBrush(QColor("#264F78")))
        rect.setPen(QPen(Qt.NoPen))
        return rect