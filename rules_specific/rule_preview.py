from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QScrollArea, QFrame
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen


class RulePreviewWidget(QWidget):
    """Widget para previsualizar el efecto de las reglas"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_rule = None
        self.tile_size = 32
        self.grid_size = 7  # Tamaño de la grilla de previsualización
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Título
        title = QLabel("Rule Preview")
        title.setStyleSheet("color: #CCCCCC; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Scroll area para la previsualización
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1E1E1E;
                border: 1px solid #454545;
            }
        """)

        # Widget principal de previsualización
        self.preview_container = QWidget()
        self.preview_container.setStyleSheet("background-color: #1E1E1E;")
        self.preview_layout = QVBoxLayout(self.preview_container)

        # Grid de previsualización
        self.grid = PreviewGrid(self.grid_size, self.tile_size)
        self.preview_layout.addWidget(self.grid)

        # Descripción de la regla
        self.rule_description = QLabel()
        self.rule_description.setWordWrap(True)
        self.rule_description.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                padding: 10px;
                background-color: #252526;
                border-radius: 5px;
            }
        """)
        self.preview_layout.addWidget(self.rule_description)

        scroll.setWidget(self.preview_container)
        layout.addWidget(scroll)

    def update_preview(self, rule_data, selected_tiles):
        """Actualiza la previsualización basada en la regla actual"""
        self.current_rule = rule_data
        if not rule_data:
            self.rule_description.setText("No rule selected")
            self.grid.clear_preview()
            return

        # Actualizar descripción
        description = self.generate_rule_description(rule_data)
        self.rule_description.setText(description)

        # Actualizar visualización según el tipo de regla
        if "rules" in rule_data:
            rules = rule_data["rules"]

            # Limpiar previsualización anterior
            self.grid.clear_preview()

            # Visualizar cada tipo de regla
            for rule_type, rule_content in rules.items():
                if rule_type == "connectivity":
                    self.preview_connectivity_rule(rule_content)
                elif rule_type == "neighbors":
                    self.preview_neighbors_rule(rule_content)
                elif rule_type == "percentage":
                    self.preview_percentage_rule(rule_content)
                # Agregar más tipos de reglas según sea necesario

    def generate_rule_description(self, rule_data):
        """Genera una descripción legible de la regla"""
        description = []

        if "rules" in rule_data:
            rules = rule_data["rules"]

            for rule_type, content in rules.items():
                if rule_type == "connectivity":
                    desc = "Connectivity Rule:\n"
                    if content.get("mustBeConnected"):
                        desc += "- Tiles must be connected\n"
                        if "connectionType" in content:
                            desc += f"- Connection type: {content['connectionType']}\n"
                    description.append(desc)

                elif rule_type == "neighbors":
                    desc = "Neighbor Rules:\n"
                    if "allowedNeighbors" in content:
                        desc += f"- Allowed neighbors: {', '.join(content['allowedNeighbors'])}\n"
                    if "forbiddenNeighbors" in content:
                        desc += f"- Forbidden neighbors: {', '.join(content['forbiddenNeighbors'])}\n"
                    description.append(desc)

                elif rule_type == "percentage":
                    desc = "Percentage Rules:\n"
                    if "min" in content:
                        desc += f"- Minimum: {content['min']}%\n"
                    if "max" in content:
                        desc += f"- Maximum: {content['max']}%\n"
                    description.append(desc)

        return "\n".join(description) if description else "No rules defined"

    def preview_connectivity_rule(self, rule_content):
        """Visualiza regla de conectividad"""
        if rule_content.get("mustBeConnected"):
            # Mostrar ejemplo de tiles conectados
            center = self.grid_size // 2
            self.grid.set_tile_type(center, center, "selected")
            self.grid.set_tile_type(center + 1, center, "connected")
            self.grid.set_tile_type(center - 1, center, "connected")

            if rule_content.get("connectionType") == "diagonal":
                self.grid.set_tile_type(center + 1, center + 1, "connected")
            elif rule_content.get("connectionType") == "both":
                self.grid.set_tile_type(center + 1, center + 1, "connected")
                self.grid.set_tile_type(center, center + 1, "connected")

    def preview_neighbors_rule(self, rule_content):
        """Visualiza regla de vecinos"""
        center = self.grid_size // 2
        self.grid.set_tile_type(center, center, "selected")

        if "allowedNeighbors" in rule_content:
            positions = [(center - 1, center), (center + 1, center),
                         (center, center - 1), (center, center + 1)]
            for x, y in positions:
                self.grid.set_tile_type(x, y, "allowed")

        if "forbiddenNeighbors" in rule_content:
            positions = [(center - 1, center - 1), (center + 1, center - 1),
                         (center - 1, center + 1), (center + 1, center + 1)]
            for x, y in positions:
                self.grid.set_tile_type(x, y, "forbidden")

    def preview_percentage_rule(self, rule_content):
        """Visualiza regla de porcentaje"""
        if "target" in rule_content:
            target = rule_content["target"]
            total_cells = self.grid_size * self.grid_size
            cells_to_fill = int((total_cells * target) / 100)

            for i in range(cells_to_fill):
                x = i % self.grid_size
                y = i // self.grid_size
                self.grid.set_tile_type(x, y, "percentage")


class PreviewGrid(QFrame):
    """Grid para mostrar la previsualización de reglas"""

    def __init__(self, size, tile_size):
        super().__init__()
        self.size = size
        self.tile_size = tile_size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.setMinimumSize(size * tile_size, size * tile_size)
        self.setStyleSheet("background-color: #1E1E1E; border: 1px solid #454545;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dibujar grid
        pen = QPen(QColor("#353535"))
        pen.setWidth(1)
        painter.setPen(pen)

        # Colores para diferentes tipos de tiles
        colors = {
            "selected": QColor("#264F78"),
            "connected": QColor("#2C7A3D"),
            "allowed": QColor("#4F784F"),
            "forbidden": QColor("#783535"),
            "percentage": QColor("#4F4F78")
        }

        # Dibujar tiles
        for x in range(self.size):
            for y in range(self.size):
                rect = self.get_tile_rect(x, y)

                # Dibujar fondo del tile
                if self.grid[y][x] in colors:
                    painter.fillRect(rect, colors[self.grid[y][x]])

                # Dibujar borde del tile
                painter.drawRect(rect)

    def get_tile_rect(self, x, y):
        return QRect(x * self.tile_size, y * self.tile_size,
                     self.tile_size - 1, self.tile_size - 1)

    def set_tile_type(self, x, y, tile_type):
        """Establece el tipo de un tile en la posición especificada"""
        if 0 <= x < self.size and 0 <= y < self.size:
            self.grid[y][x] = tile_type
            self.update()

    def clear_preview(self):
        """Limpia la previsualización"""
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.update()