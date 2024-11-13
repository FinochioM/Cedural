from PySide6.QtWidgets import (QMainWindow, QHBoxLayout, QWidget, QSplitter,
                               QVBoxLayout, QSizePolicy, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt
from .panels.tileset_panel import TilesetPanel
from .panels.preview_panel import PreviewPanel
from .panels.settings_panel import SettingsPanel
from .panels.workspace_panel import WorkspacePanel
from .menu.main_menu import MainMenu
from managers .workspaces_managers.project_creation import ProjectCreationDialog
from managers.workspaces_managers.project_management import Project, ProjectType
from pathlib import Path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_project = None
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle("Cedural - Tilemaps Generator")
        self.setMinimumSize(1280, 720)

        # Menu bar con nuevas acciones
        self.menu_bar = MainMenu(self)
        self.setMenuBar(self.menu_bar)

        # Central widget y layout principal (igual que antes)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # Main splitter y paneles (igual que antes)
        main_splitter = QSplitter(Qt.Horizontal)

        # Left container with vertical splitter
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Vertical splitter for tileset and workspace panels
        vertical_splitter = QSplitter(Qt.Vertical)

        # Create panels
        self.settings_panel = SettingsPanel()
        self.tileset_panel = TilesetPanel(self.settings_panel)
        self.preview_panel = PreviewPanel()
        self.workspace_panel = WorkspacePanel()

        # Add panels to splitters
        vertical_splitter.addWidget(self.tileset_panel)
        vertical_splitter.addWidget(self.workspace_panel)

        left_layout.addWidget(vertical_splitter)

        main_splitter.addWidget(left_container)
        main_splitter.addWidget(self.preview_panel)
        main_splitter.addWidget(self.settings_panel)

        main_splitter.setSizes([100, 950, 150])

        main_layout.addWidget(main_splitter)

        # Update window title
        self.update_window_title()

    def setup_connections(self):
        """Configura las conexiones de señales/slots"""
        # Conectar acciones del menú
        self.menu_bar.new_project_action.triggered.connect(self.create_new_project)
        self.menu_bar.open_project_action.triggered.connect(self.open_project)
        self.menu_bar.save_project_action.triggered.connect(self.save_project)
        self.menu_bar.save_as_action.triggered.connect(self.save_project_as)

        # Conectar paneles - Corregido el nombre de la señal
        self.workspace_panel.workspaceChanged.connect(self.on_workspace_changed)
        self.workspace_panel.roomSelected.connect(self.on_room_selected)

        # Conectar selección de tiles
        self.tileset_panel.tilesSelected.connect(self.settings_panel.update_tile_selection)

    def create_new_project(self):
        """Crea un nuevo proyecto"""
        dialog = ProjectCreationDialog(self)
        if dialog.exec():
            project_data = dialog.get_project_data()

            # Crear nuevo proyecto
            self.current_project = Project(
                name=project_data["name"],
                project_type=ProjectType(project_data["type"])
            )

            # Actualizar configuraciones del proyecto
            self.current_project.settings["grid"].width = project_data["grid"]["width"]
            self.current_project.settings["grid"].height = project_data["grid"]["height"]
            self.current_project.settings["default_room"].width = project_data["default_room"]["width"]
            self.current_project.settings["default_room"].height = project_data["default_room"]["height"]

            # Actualizar UI
            self.workspace_panel.set_project(self.current_project)
            self.update_window_title()
            self.update_ui_for_project_type()

            # Habilitar acciones del menú
            self.menu_bar.save_project_action.setEnabled(True)
            self.menu_bar.save_as_action.setEnabled(True)
            self.menu_bar.export_action.setEnabled(True)

    def open_project(self):
        """Abre un proyecto existente"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "Project Files (project.json);;All Files (*)"
        )

        if file_path:
            try:
                self.current_project = Project.load(Path(file_path).parent)
                self.workspace_panel.set_project(self.current_project)
                self.update_window_title()
                self.update_ui_for_project_type()

                # Habilitar acciones del menú
                self.menu_bar.save_project_action.setEnabled(True)
                self.menu_bar.save_as_action.setEnabled(True)
                self.menu_bar.export_action.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to open project: {str(e)}"
                )

    def save_project(self):
        """Guarda el proyecto actual"""
        if not self.current_project:
            return

        try:
            self.current_project.save(Path("."))
            QMessageBox.information(
                self,
                "Success",
                "Project saved successfully!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save project: {str(e)}"
            )

    def save_project_as(self):
        """Guarda el proyecto con un nuevo nombre/ubicación"""
        if not self.current_project:
            return

        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Save Project As",
            ""
        )

        if dir_path:
            try:
                self.current_project.save(Path(dir_path))
                QMessageBox.information(
                    self,
                    "Success",
                    "Project saved successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save project: {str(e)}"
                )

    def update_window_title(self):
        """Actualiza el título de la ventana con el nombre del proyecto"""
        base_title = "Cedural - Tilemaps Generator"
        if self.current_project:
            self.setWindowTitle(f"{base_title} - {self.current_project.name}")
        else:
            self.setWindowTitle(base_title)

    def update_ui_for_project_type(self):
        """Actualiza la UI basada en el tipo de proyecto"""
        if not self.current_project:
            return

        # Actualizar configuraciones de grid
        self.settings_panel.update_grid_settings(
            self.current_project.settings["grid"]
        )

        # Actualizar preview según tipo de proyecto
        self.preview_panel.set_project_type(self.current_project.type)

        # Actualizar panel de reglas si es necesario
        self.settings_panel.update_for_project_type(self.current_project.type)

    def on_workspace_changed(self, workspace_id):
        """Maneja cambios en el workspace actual"""
        if self.current_project and workspace_id in self.current_project.workspaces:
            workspace = self.current_project.workspaces[workspace_id]
            # Actualizar UI según el workspace
            self.update_ui_for_workspace(workspace)

    def on_room_selected(self, workspace_id, room_id):
        """Maneja la selección de una room"""
        if self.current_project and workspace_id in self.current_project.workspaces:
            workspace = self.current_project.workspaces[workspace_id]
            if room_id in workspace.rooms:
                room = workspace.rooms[room_id]
                # Actualizar preview y configuraciones
                self.preview_panel.load_room(room)
                self.settings_panel.load_room_settings(room)

    def update_ui_for_workspace(self, workspace):
        """Actualiza la UI basada en el workspace actual"""
        # Actualizar tileset si es necesario
        if workspace.tileset:
            self.tileset_panel.load_tileset(workspace.tileset)

        # Actualizar otras configuraciones específicas del workspace
        self.settings_panel.update_for_workspace(workspace)