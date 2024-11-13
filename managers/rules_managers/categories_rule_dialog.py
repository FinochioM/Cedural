from PySide6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QDialogButtonBox,
                               QFileDialog, QMessageBox, QWidget, QLabel, QSplitter, QTreeWidget, QTreeWidgetItem, QInputDialog)
from PySide6.QtCore import Qt
import json
import os

from rules_specific.editor_dialog import JsonEditorDialog
from managers.rules_managers.rule_definition import RulesCatalog
from rules_specific.rule_preview import RulePreviewWidget
from rules_specific.rule_template_manager import RuleTemplateManager
from rules_specific.rule_validator import RuleValidator


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
        self.rules_dir = ""  # Directorio donde se guardan los archivos JSON
        self.template_manager = RuleTemplateManager()
        self.init_ui()
        self.ensure_rules_directory()
        self.load_rule_files()

    def init_ui(self):
        self.setWindowTitle(f"Rules for {self.category_name}")
        self.setModal(True)
        self.resize(1000, 600)  # Aumentamos el tamaño para acomodar la previsualización

        # Main layout
        main_layout = QVBoxLayout(self)

        # Horizontal splitter for main content
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel (tree and buttons)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Tree widget for rules_managers
        rules_title = QLabel("Rule Files")
        rules_title.setStyleSheet("color: #CCCCCC; font-weight: bold;")
        left_layout.addWidget(rules_title)

        self.rules_tree = RuleTreeWidget()
        self.rules_tree.setHeaderLabels(["Rules"])
        self.rules_tree.itemSelectionChanged.connect(self.on_rule_selected)
        left_layout.addWidget(self.rules_tree)

        # Buttons panel
        buttons_panel = QWidget()
        buttons_layout = QVBoxLayout(buttons_panel)

        # Action buttons
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

        create_button = QPushButton("Create New Rule")
        edit_button = QPushButton("Edit Rule")
        save_template_button = QPushButton("Save as Template")
        load_template_button = QPushButton("Load Template")
        delete_button = QPushButton("Delete Rule")

        for button in [create_button, edit_button, save_template_button,
                       load_template_button, delete_button]:
            button.setStyleSheet(button_style)

        create_button.clicked.connect(self.create_new_rule)
        edit_button.clicked.connect(self.edit_rule)
        save_template_button.clicked.connect(self.save_as_template)
        load_template_button.clicked.connect(self.load_from_template)
        delete_button.clicked.connect(self.delete_rule)

        buttons_layout.addWidget(create_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(save_template_button)
        buttons_layout.addWidget(load_template_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()

        left_layout.addWidget(buttons_panel)

        # Right panel (preview)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        preview_title = QLabel("Rule Preview")
        preview_title.setStyleSheet("color: #CCCCCC; font-weight: bold;")
        right_layout.addWidget(preview_title)

        self.preview_widget = RulePreviewWidget()
        right_layout.addWidget(self.preview_widget)

        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 600])

        # Add splitter to main layout
        main_layout.addWidget(main_splitter)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def ensure_rules_directory(self):
        """Asegura que existe el directorio para las reglas"""
        # Obtener la ruta absoluta
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.rules_dir = os.path.join(current_dir, "rules_managers")

        os.makedirs(self.rules_dir, exist_ok=True)
    def load_rule_files(self):
        """Carga todos los archivos JSON de reglas para esta categoría"""
        self.rules_tree.clear()

        # Mostrar todos los archivos en el directorio
        all_files = os.listdir(self.rules_dir)

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

                self.load_rule_files()

                self.select_file_in_tree(file_path)

                QMessageBox.information(self, "Success", "Rule file created successfully!")
            except Exception as e:
                print(f"Error creating file: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to create rule file: {str(e)}")

    def select_file_in_tree(self, file_path):
        """Busca y selecciona un archivo específico en el árbol"""
        root = self.rules_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.data(0, Qt.UserRole) == file_path:
                self.rules_tree.setCurrentItem(item)
                break

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
                json_data = json.load(f)

            if self.validate_rule(json_data):
                # Abrir el editor
                editor = JsonEditorDialog(json_data, self)
                if editor.exec() == QDialog.Accepted:
                    edited_data = editor.get_json()
                    if edited_data:
                        # Validar el JSON editado
                        if self.validate_rule(edited_data):
                            # Guardar cambios
                            with open(file_path, 'w') as f:
                                json.dump(edited_data, f, indent=2)
                            self.load_rule_files()  # Recargar archivos
                            self.select_file_in_tree(file_path)  # Re-seleccionar el archivo
                            QMessageBox.information(self, "Success", "Rule file saved successfully!")
                        else:
                            QMessageBox.warning(self, "Invalid Rule",
                                             "The edited rule does not follow the required structure.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit rule file: {str(e)}")


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

    def on_rule_selected(self):
        """Actualiza la previsualización cuando se selecciona una regla"""
        current_item = self.rules_tree.currentItem()
        if current_item:
            # Obtener el archivo raíz si se seleccionó un subelemento
            while current_item.parent():
                current_item = current_item.parent()

            file_path = current_item.data(0, Qt.UserRole)
            if file_path:
                try:
                    with open(file_path, 'r') as f:
                        rule_data = json.load(f)
                        self.preview_widget.update_preview(rule_data, [])  # Actualizar preview
                except Exception as e:
                    print(f"Error loading rule for preview: {str(e)}")

    def validate_rule(self, rule_data):
        """Valida una regla usando RuleValidator"""
        validation_results = RuleValidator.validate_rule_structure(rule_data)

        if not validation_results["is_valid"]:
            error_msg = "\n".join(validation_results["errors"])
            QMessageBox.warning(self, "Invalid Rule", f"Validation errors:\n{error_msg}")

        if validation_results["warnings"]:
            warning_msg = "\n".join(validation_results["warnings"])
            QMessageBox.warning(self, "Rule Warnings", f"Warnings:\n{warning_msg}")

        return validation_results["is_valid"]

    def save_as_template(self):
        """Guarda la regla actual como template"""
        current_item = self.rules_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a rule to save as template")
            return

        # Obtener el archivo raíz
        while current_item.parent():
            current_item = current_item.parent()

        file_path = current_item.data(0, Qt.UserRole)
        if not file_path:
            return

        template_name, ok = QInputDialog.getText(
            self, "Save Template", "Enter template name:"
        )

        if ok and template_name:
            try:
                with open(file_path, 'r') as f:
                    rule_data = json.load(f)

                if self.template_manager.save_as_template(rule_data, template_name):
                    QMessageBox.information(
                        self, "Success", "Template saved successfully!"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to save template: {str(e)}"
                )

    def load_from_template(self):
        """Carga una regla desde un template"""
        templates = self.template_manager.get_available_templates()
        if not templates:
            QMessageBox.information(
                self, "Templates", "No templates available"
            )
            return

        template_name, ok = QInputDialog.getItem(
            self, "Load Template", "Select template:", templates, 0, False
        )

        if ok and template_name:
            rule_data = self.template_manager.load_template(template_name)
            if rule_data:
                self.create_new_rule(template_data=rule_data)