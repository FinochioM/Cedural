from PySide6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QDialogButtonBox,
                               QFileDialog, QMessageBox, QWidget, QHBoxLayout,
                               QLabel, QSplitter, QTreeWidget, QTreeWidgetItem)
from PySide6.QtCore import Qt
import json
import os
from managers.rule_definition import RulesCatalog


class RuleTreeWidget(QTreeWidget):
    """Widget para mostrar el contenido de los archivos JSON de reglas"""

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Rule Files / Content"])
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #1E1E1E;
                border: 1px solid #454545;
                color: #CCCCCC;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #264F78;
            }
            QTreeWidget::item:hover {
                background-color: #2D2D2D;
            }
            QTreeWidget::branch {
                background-color: #1E1E1E;
            }
        """)

    def add_json_content(self, file_name, json_data):
        """Agrega el contenido de un archivo JSON al árbol"""
        # Crear item principal para el archivo
        file_item = QTreeWidgetItem(self)
        file_item.setText(0, os.path.basename(file_name))
        file_item.setData(0, Qt.UserRole, file_name)  # Guardar ruta completa

        # Agregar contenido del JSON
        self._add_json_node(json_data, file_item)

        # Expandir el item
        file_item.setExpanded(True)

    def _add_json_node(self, data, parent_item):
        """Recursivamente agrega nodos para el contenido JSON"""
        if isinstance(data, dict):
            for key, value in data.items():
                item = QTreeWidgetItem(parent_item)
                if isinstance(value, (dict, list)):
                    item.setText(0, key)
                    self._add_json_node(value, item)
                else:
                    item.setText(0, f"{key}: {value}")
        elif isinstance(data, list):
            for i, value in enumerate(data):
                item = QTreeWidgetItem(parent_item)
                if isinstance(value, (dict, list)):
                    item.setText(0, f"[{i}]")
                    self._add_json_node(value, item)
                else:
                    item.setText(0, str(value))


class CategoryRulesDialog(QDialog):
    def __init__(self, category_name, category_manager, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.category_manager = category_manager
        self.rules_dir = "rules"  # Directorio donde se guardan los archivos JSON
        self.init_ui()
        self.ensure_rules_directory()
        self.load_rule_files()

    def init_ui(self):
        self.setWindowTitle(f"Rules for {self.category_name}")
        self.setModal(True)
        self.resize(800, 500)

        # Main layout
        layout = QVBoxLayout(self)

        # Crear un splitter horizontal
        splitter = QSplitter(Qt.Horizontal)

        # Panel izquierdo - Vista de archivos y reglas
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Título
        rules_title = QLabel("Rule Files")
        rules_title.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        left_layout.addWidget(rules_title)

        # Tree widget para mostrar archivos y su contenido
        self.rules_tree = RuleTreeWidget()
        left_layout.addWidget(self.rules_tree)

        # Panel derecho - Botones de acción
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        actions_title = QLabel("Actions")
        actions_title.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        right_layout.addWidget(actions_title)

        # Botones
        button_style = """
            QPushButton {
                background-color: #264F78;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                color: white;
                min-width: 80px;
                min-height: 30px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #365F88;
            }
        """

        create_button = QPushButton("Create New Rule File")
        edit_button = QPushButton("Edit Rule File")
        delete_button = QPushButton("Delete Rule File")

        create_button.setStyleSheet(button_style)
        edit_button.setStyleSheet(button_style)
        delete_button.setStyleSheet(button_style)

        create_button.clicked.connect(self.create_new_rule)
        edit_button.clicked.connect(self.edit_rule)
        delete_button.clicked.connect(self.delete_rule)

        right_layout.addWidget(create_button)
        right_layout.addWidget(edit_button)
        right_layout.addWidget(delete_button)
        right_layout.addStretch()

        # Agregar paneles al splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([550, 250])

        # Agregar splitter al layout principal
        layout.addWidget(splitter)

        # Botones del diálogo
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
            QSplitter::handle {
                background-color: #353535;
                width: 2px;
            }
        """)

    def ensure_rules_directory(self):
        """Asegura que existe el directorio para las reglas"""
        os.makedirs(self.rules_dir, exist_ok=True)

    def load_rule_files(self):
        """Carga todos los archivos JSON de reglas para esta categoría"""
        self.rules_tree.clear()

        if not os.path.exists(self.rules_dir):
            return

        # Filtrar por prefijo de categoría
        rule_files = [f for f in os.listdir(self.rules_dir)
                      if f.startswith(f"{self.category_name}_") and f.endswith(".json")]

        for filename in rule_files:
            file_path = os.path.join(self.rules_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                    self.rules_tree.add_json_content(file_path, json_data)
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")

    def create_new_rule(self):
        """Crea un nuevo archivo JSON con el template de reglas"""
        # Generar un nombre único para el archivo
        base_name = f"{self.category_name}_rule"
        counter = 1
        while os.path.exists(os.path.join(self.rules_dir, f"{base_name}_{counter}.json")):
            counter += 1

        suggested_filename = f"{base_name}_{counter}.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Rule File",
            os.path.join(self.rules_dir, suggested_filename),
            "JSON Files (*.json)"
        )

        if file_path:
            # Verificar que el nombre del archivo comience con el nombre de la categoría
            file_name = os.path.basename(file_path)
            if not file_name.startswith(f"{self.category_name}_"):
                file_path = os.path.join(
                    os.path.dirname(file_path),
                    f"{self.category_name}_{file_name}"
                )

            template = RulesCatalog.generate_template()
            template["category"] = self.category_name

            try:
                with open(file_path, 'w') as f:
                    json.dump(template, f, indent=2)
                self.load_rule_files()  # Recargar los archivos
                QMessageBox.information(self, "Success", "Rule file created successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create rule file: {str(e)}")

    def edit_rule(self):
        """Edita el archivo JSON seleccionado"""
        current_item = self.rules_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a rule file to edit")
            return

        # Obtener el archivo raíz si se seleccionó un subelemento
        while current_item.parent():
            current_item = current_item.parent()

        file_path = current_item.data(0, Qt.UserRole)
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                rule_data = json.load(f)

            if RulesCatalog.validate_rule(rule_data):
                # Aquí iría la lógica para editar el archivo
                # Por ahora solo mostramos un mensaje
                QMessageBox.information(
                    self,
                    "Edit Rule",
                    f"Editing file: {os.path.basename(file_path)}\n"
                    "Editor functionality coming soon..."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Rule",
                    "The rule file does not follow the required structure."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load rule file: {str(e)}"
            )

    def delete_rule(self):
        """Elimina el archivo JSON seleccionado"""
        current_item = self.rules_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a rule file to delete")
            return

        # Obtener el archivo raíz si se seleccionó un subelemento
        while current_item.parent():
            current_item = current_item.parent()

        file_path = current_item.data(0, Qt.UserRole)
        if not file_path:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {os.path.basename(file_path)}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                os.remove(file_path)
                self.load_rule_files()  # Recargar los archivos
                QMessageBox.information(self, "Success", "Rule file deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete rule file: {str(e)}")
