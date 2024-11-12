from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGridLayout,
                               QScrollArea, QFrame)
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush


class RulePreviewWidget(QWidget):
    """Widget para previsualizar el efecto de las reglas"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_rule = None
        self.tile_size = 32
        self.grid_size = 7
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

        # Grid de previsualización mejorado
        self.grid = PreviewGrid(self.grid_size, self.tile_size)
        self.preview_layout.addWidget(self.grid)

        # Descripción de la regla con formato mejorado
        self.rule_description = QLabel()
        self.rule_description.setWordWrap(True)
        self.rule_description.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                padding: 10px;
                background-color: #252526;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 12px;
            }
        """)
        self.preview_layout.addWidget(self.rule_description)

        # Leyenda de colores
        self.legend = ColorLegend()
        self.preview_layout.addWidget(self.legend)

        scroll.setWidget(self.preview_container)
        layout.addWidget(scroll)

    def _preview_percentage_rule(self, content):
        """Visualiza reglas de porcentaje mostrando una distribución ejemplo"""
        min_percent = content.get('min', 0)
        max_percent = content.get('max', 100)
        target = content.get('target', (min_percent + max_percent) / 2)

        # Calcular cuántos tiles representar basado en el target o el punto medio
        total_cells = self.grid_size * self.grid_size
        target_cells = int((target / 100) * total_cells)

        # Marcar tiles para representar el porcentaje objetivo
        cells_marked = 0
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if cells_marked < target_cells:
                    self.grid.set_tile_type(x, y, "selected")
                    cells_marked += 1

        # Marcar algunos tiles adicionales como "allowed" para mostrar el rango máximo
        if max_percent > target:
            max_cells = int((max_percent / 100) * total_cells)
            additional_cells = max_cells - target_cells
            cells_marked = 0
            for y in range(self.grid_size):
                for x in range(self.grid_size):
                    if self.grid.grid[y][x] is None and cells_marked < additional_cells:
                        self.grid.set_tile_type(x, y, "allowed")
                        cells_marked += 1

        # Marcar algunos tiles como "forbidden" para mostrar el límite mínimo
        if min_percent > 0:
            min_cells = int((min_percent / 100) * total_cells)
            required_remaining = min_cells - target_cells
            if required_remaining > 0:
                cells_marked = 0
                for y in range(self.grid_size - 1, -1, -1):
                    for x in range(self.grid_size - 1, -1, -1):
                        if self.grid.grid[y][x] is None and cells_marked < required_remaining:
                            self.grid.set_tile_type(x, y, "required")
                            cells_marked += 1

    def update_preview(self, rule_data, selected_tiles):
        """Actualiza la previsualización basada en la regla actual"""
        self.current_rule = rule_data
        if not rule_data:
            self.rule_description.setText("No rule selected")
            self.grid.clear_preview()
            return

        self.grid.clear_preview()

        if "rules" in rule_data:
            rules = rule_data["rules"]
            description_parts = []

            for rule_type, content in rules.items():
                if rule_type == "connectivity":
                    self._preview_connectivity_rule(content)
                    description_parts.append(self._format_connectivity_description(content))

                elif rule_type == "neighbors":
                    self._preview_neighbors_rule(content)
                    description_parts.append(self._format_neighbors_description(content))

                elif rule_type == "percentage":
                    self._preview_percentage_rule(content)
                    description_parts.append(self._format_percentage_description(content))

                elif rule_type == "pattern":
                    self._preview_pattern_rule(content)
                    description_parts.append(self._format_pattern_description(content))

                elif rule_type == "symmetry":
                    self._preview_symmetry_rule(content)
                    description_parts.append(self._format_symmetry_description(content))

                elif rule_type == "border":
                    self._preview_border_rule(content)
                    description_parts.append(self._format_border_description(content))

            # Actualizar descripción con formato mejorado
            self.rule_description.setText("\n\n".join(description_parts))

    def _preview_connectivity_rule(self, content):
        """Visualiza regla de conectividad con ejemplos más claros"""
        if content.get("mustBeConnected"):
            center = self.grid_size // 2
            # Mostrar un patrón de conectividad más claro
            self.grid.set_tile_type(center, center, "selected")

            connection_type = content.get("connectionType", "orthogonal")
            if connection_type == "orthogonal" or connection_type == "both":
                self.grid.set_tile_type(center + 1, center, "connected")
                self.grid.set_tile_type(center - 1, center, "connected")
                self.grid.set_tile_type(center, center + 1, "connected")
                self.grid.set_tile_type(center, center - 1, "connected")

            if connection_type == "diagonal" or connection_type == "both":
                self.grid.set_tile_type(center + 1, center + 1, "connected")
                self.grid.set_tile_type(center - 1, center - 1, "connected")
                self.grid.set_tile_type(center + 1, center - 1, "connected")
                self.grid.set_tile_type(center - 1, center + 1, "connected")

    def _preview_neighbors_rule(self, content):
        """Visualiza regla de vecinos con patrones más claros"""
        center = self.grid_size // 2
        self.grid.set_tile_type(center, center, "selected")

        if "allowedNeighbors" in content:
            positions = [
                (center - 1, center), (center + 1, center),
                (center, center - 1), (center, center + 1)
            ]
            for x, y in positions:
                self.grid.set_tile_type(x, y, "allowed")

        if "forbiddenNeighbors" in content:
            positions = [
                (center - 1, center - 1), (center + 1, center - 1),
                (center - 1, center + 1), (center + 1, center + 1)
            ]
            for x, y in positions:
                self.grid.set_tile_type(x, y, "forbidden")

    def _preview_pattern_rule(self, content):
        """Visualiza reglas de patrón"""
        if "requiredPatterns" in content:
            # Mostrar un ejemplo del patrón requerido
            pattern = content["requiredPatterns"][0] if content["requiredPatterns"] else None
            if pattern:
                self._display_pattern(pattern, "required")

    def _preview_symmetry_rule(self, content):
        """Visualiza reglas de simetría"""
        symmetry_type = content.get("type")
        center = self.grid_size // 2

        if symmetry_type == "horizontal":
            for i in range(3):
                self.grid.set_tile_type(center - 1 + i, center - 2, "symmetry")
                self.grid.set_tile_type(center - 1 + i, center + 2, "symmetry")
        elif symmetry_type == "vertical":
            for i in range(3):
                self.grid.set_tile_type(center - 2, center - 1 + i, "symmetry")
                self.grid.set_tile_type(center + 2, center - 1 + i, "symmetry")

    def _preview_border_rule(self, content):
        """Visualiza reglas de borde"""
        if content.get("mustBeBorder"):
            for i in range(self.grid_size):
                if "top" in content.get("borderSides", []):
                    self.grid.set_tile_type(i, 0, "border")
                if "bottom" in content.get("borderSides", []):
                    self.grid.set_tile_type(i, self.grid_size - 1, "border")
                if "left" in content.get("borderSides", []):
                    self.grid.set_tile_type(0, i, "border")
                if "right" in content.get("borderSides", []):
                    self.grid.set_tile_type(self.grid_size - 1, i, "border")

    def _format_connectivity_description(self, content):
        return f"""<b>Connectivity Rule</b>
• Must be connected: {content.get('mustBeConnected', False)}
• Connection type: {content.get('connectionType', 'orthogonal')}"""

    def _format_neighbors_description(self, content):
        allowed = ', '.join(content.get('allowedNeighbors', []))
        forbidden = ', '.join(content.get('forbiddenNeighbors', []))
        return f"""<b>Neighbor Rules</b>
• Allowed neighbors: {allowed or 'None'}
• Forbidden neighbors: {forbidden or 'None'}"""

    def _format_percentage_description(self, content):
        return f"""<b>Percentage Rules</b>
• Minimum: {content.get('min', 0)}%
• Maximum: {content.get('max', 100)}%
• Target: {content.get('target', '-')}%"""

    def _format_pattern_description(self, content):
        return f"""<b>Pattern Rules</b>
• Required patterns: {len(content.get('requiredPatterns', []))}
• Forbidden patterns: {len(content.get('forbiddenPatterns', []))}"""

    def _format_symmetry_description(self, content):
        return f"""<b>Symmetry Rules</b>
• Type: {content.get('type', 'none')}
• Strictness: {content.get('strictness', 1.0)}"""

    def _format_border_description(self, content):
        sides = ', '.join(content.get('borderSides', []))
        return f"""<b>Border Rules</b>
• Must be border: {content.get('mustBeBorder', False)}
• Border sides: {sides or 'all'}
• Width: {content.get('borderWidth', 1)}"""


class PreviewGrid(QFrame):
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

        # Colores mejorados para mejor visibilidad
        colors = {
            "selected": QColor("#264F78"),  # Azul selección
            "connected": QColor("#2C7A3D"),  # Verde conexión
            "allowed": QColor("#4F784F"),  # Verde permitido
            "forbidden": QColor("#783535"),  # Rojo prohibido
            "border": QColor("#787832"),  # Amarillo borde
            "symmetry": QColor("#4F4F78"),  # Azul simetría
            "pattern": QColor("#784F78"),  # Morado patrón
            "required": QColor("#32785F")  # Verde azulado requerido
        }

        # Dibujar grid base
        painter.setPen(QPen(QColor("#353535")))

        for x in range(self.size):
            for y in range(self.size):
                rect = QRect(x * self.tile_size, y * self.tile_size,
                             self.tile_size - 1, self.tile_size - 1)

                # Dibujar fondo del tile
                if self.grid[y][x] in colors:
                    painter.fillRect(rect, colors[self.grid[y][x]])

                    # Agregar patrón o textura según el tipo
                    if self.grid[y][x] in ["pattern", "required"]:
                        self._draw_pattern(painter, rect)
                    elif self.grid[y][x] == "symmetry":
                        self._draw_symmetry_marker(painter, rect)

                # Dibujar borde del tile
                painter.drawRect(rect)

    def _draw_pattern(self, painter, rect):
        """Dibuja un patrón de líneas diagonales para tiles de patrón"""
        pen = painter.pen()
        pen.setColor(QColor("#CCCCCC"))
        painter.setPen(pen)
        painter.drawLine(rect.topLeft(), rect.bottomRight())
        painter.drawLine(rect.topRight(), rect.bottomLeft())

    def _draw_symmetry_marker(self, painter, rect):
        """Dibuja un marcador específico para tiles simétricos"""
        pen = painter.pen()
        pen.setColor(QColor("#CCCCCC"))
        painter.setPen(pen)
        center = rect.center()
        size = min(rect.width(), rect.height()) // 4
        painter.drawEllipse(center, size, size)

    def set_tile_type(self, x, y, tile_type):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.grid[y][x] = tile_type
            self.update()

    def clear_preview(self):
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.update()


class ColorLegend(QFrame):
    """Leyenda que muestra el significado de cada color"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border-radius: 5px;
                padding: 5px;
                margin-top: 10px;
            }
        """)

        layout = QGridLayout(self)
        layout.setSpacing(5)

        legend_items = [
            ("Selected Tile", "#264F78"),
            ("Connected", "#2C7A3D"),
            ("Allowed", "#4F784F"),
            ("Forbidden", "#783535"),
            ("Border", "#787832"),
            ("Symmetry", "#4F4F78"),
            ("Pattern", "#784F78"),
            ("Required", "#32785F")
        ]

        for i, (text, color) in enumerate(legend_items):
            color_box = QFrame()
            color_box.setFixedSize(16, 16)
            color_box.setStyleSheet(f"background-color: {color}; border: 1px solid #454545;")