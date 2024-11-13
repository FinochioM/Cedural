from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeWidget,
                               QTreeWidgetItem, QPushButton, QMenu, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from .base_panel import BasePanel
from managers.workspaces_managers.project_management import Project, Workspace, Room

class WorkspaceTree(QTreeWidget):
    """Tree widget for displaying workspaces and rooms"""
    workspaceChanged = Signal(str)  # Emite workspace_id
    roomSelected = Signal(str, str)  # Emite (workspace_id, room_id)
    workspaceDeleted = Signal(str)  # Nueva señal para workspace eliminado
    roomDeleted = Signal(str, str)  # Nueva señal para room eliminada
    workspaceRenamed = Signal(str, str)  # Nueva señal para workspace renombrado
    roomRenamed = Signal(str, str, str)  # Nueva señal para room renombrada

    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #1E1E1E;
                border: 1px solid #454545;
            }
            QTreeWidget::item {
                padding: 5px;
                border-radius: 3px;
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

        # Conectar selección
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.itemChanged.connect(self.on_item_changed)  # Para renombrar

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2D2D2D;
                border: 1px solid #454545;
            }
            QMenu::item {
                padding: 5px 20px;
                color: #CCCCCC;
            }
            QMenu::item:selected {
                background-color: #264F78;
            }
            QMenu::separator {
                height: 1px;
                background-color: #454545;
                margin: 4px 0px;
            }
        """)

        if item is None:
            # Menu para cuando no hay item seleccionado
            new_workspace = menu.addAction("New Workspace")
            new_workspace.triggered.connect(self.create_workspace)
        else:
            if item.parent() is None:
                # Menu para workspace
                new_room = menu.addAction("New Room")
                new_room.triggered.connect(lambda: self.create_room(item))
                menu.addSeparator()
                rename = menu.addAction("Rename Workspace")
                delete = menu.addAction("Delete Workspace")
                rename.triggered.connect(lambda: self.rename_item(item))
                delete.triggered.connect(lambda: self.delete_workspace(item))
            else:
                # Menu para room
                rename = menu.addAction("Rename Room")
                delete = menu.addAction("Delete Room")
                rename.triggered.connect(lambda: self.rename_item(item))
                delete.triggered.connect(lambda: self.delete_room(item))

        menu.exec_(event.globalPos())

    def on_selection_changed(self):
        """Maneja cambios en la selección del árbol"""
        current = self.currentItem()
        if not current:
            return

        # Si es un workspace
        if current.parent() is None:
            workspace_id = current.data(0, Qt.UserRole)
            self.workspaceChanged.emit(workspace_id)
        # Si es una room
        else:
            workspace_item = current.parent()
            workspace_id = workspace_item.data(0, Qt.UserRole)
            room_id = current.data(0, Qt.UserRole)
            self.roomSelected.emit(workspace_id, room_id)

    def set_project(self, project: Project):
        """Actualiza el árbol con los datos del proyecto"""
        self.clear()

        # Agregar workspaces y rooms
        for workspace in project.workspaces.values():
            workspace_item = QTreeWidgetItem(self)
            workspace_item.setText(0, f"🗀 {workspace.name}")
            workspace_item.setData(0, Qt.UserRole, workspace.id)
            workspace_item.setFlags(workspace_item.flags() | Qt.ItemIsEditable)
            workspace_item.setExpanded(True)

            # Agregar rooms del workspace
            for room in workspace.rooms.values():
                room_item = QTreeWidgetItem(workspace_item)
                room_item.setText(0, f"└ {room.name}")
                room_item.setData(0, Qt.UserRole, room.id)
                room_item.setFlags(room_item.flags() | Qt.ItemIsEditable)

    def create_workspace(self) -> str:
        """Crea un nuevo workspace y retorna su ID"""
        workspace_item = QTreeWidgetItem(self)
        workspace_item.setText(0, "🗀 New Workspace")
        workspace_item.setExpanded(True)
        self.editItem(workspace_item)
        return workspace_item.data(0, Qt.UserRole)

    def create_room(self, workspace_item) -> str:
        """Crea una nueva room en el workspace dado y retorna su ID"""
        room_item = QTreeWidgetItem(workspace_item)
        room_item.setText(0, "└ New Room")
        workspace_item.setExpanded(True)
        self.editItem(room_item)
        return room_item.data(0, Qt.UserRole)

    def rename_item(self, item):
        """Renombra un workspace o room"""
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.editItem(item)

    def delete_workspace(self, workspace_item):
        """Elimina un workspace y todas sus rooms"""
        workspace_id = workspace_item.data(0, Qt.UserRole)
        self.workspaceDeleted.emit(workspace_id)
        self.takeTopLevelItem(self.indexOfTopLevelItem(workspace_item))

    def delete_room(self, room_item):
        """Elimina una room"""
        workspace_item = room_item.parent()
        workspace_id = workspace_item.data(0, Qt.UserRole)
        room_id = room_item.data(0, Qt.UserRole)
        self.roomDeleted.emit(workspace_id, room_id)
        workspace_item.removeChild(room_item)

    def on_item_changed(self, item, column):
        """Maneja el cambio de nombre de items"""
        if not item:
            return

        new_name = item.text(0)
        # Remover los prefijos si existen
        if new_name.startswith("🗀 "):
            new_name = new_name[2:]
        elif new_name.startswith("└ "):
            new_name = new_name[2:]

        # Validar nombre
        if not new_name.strip():
            # Si el nombre está vacío, restaurar el nombre anterior
            if item.parent() is None:
                item.setText(0, f"🗀 New Workspace")
            else:
                item.setText(0, f"└ New Room")
            return

        # Quitar temporalmente la conexión para evitar recursión
        self.blockSignals(True)

        # Emitir señal según el tipo de item
        if item.parent() is None:
            # Es un workspace
            workspace_id = item.data(0, Qt.UserRole)
            self.workspaceRenamed.emit(workspace_id, new_name)
            item.setText(0, f"🗀 {new_name}")
        else:
            # Es una room
            workspace_id = item.parent().data(0, Qt.UserRole)
            room_id = item.data(0, Qt.UserRole)
            self.roomRenamed.emit(workspace_id, room_id, new_name)
            item.setText(0, f"└ {new_name}")

        # Restaurar la conexión
        self.blockSignals(False)


class WorkspacePanel(BasePanel):
    workspaceChanged = Signal(str)  # Emite workspace_id cuando cambia el workspace actual
    roomSelected = Signal(str, str)  # Emite workspace_id, room_id cuando se selecciona una room

    def __init__(self):
        super().__init__("Workspaces")
        self.current_project = None
        self.init_panel()

    def init_panel(self):
        # Workspace tree
        self.workspace_tree = WorkspaceTree()
        self.content_layout.addWidget(self.workspace_tree)

        # Conectar señales del tree
        self.workspace_tree.workspaceChanged.connect(self.workspaceChanged)
        self.workspace_tree.roomSelected.connect(self.roomSelected)
        self.workspace_tree.workspaceDeleted.connect(self.delete_workspace)
        self.workspace_tree.roomDeleted.connect(self.delete_room)
        self.workspace_tree.workspaceRenamed.connect(self.rename_workspace)
        self.workspace_tree.roomRenamed.connect(self.rename_room)

        # Set content margins
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(0)

    def set_project(self, project: Project):
        """Establece el proyecto actual y actualiza la UI"""
        self.current_project = project
        self.workspace_tree.set_project(project)

    def create_workspace(self) -> Workspace:
        """Crea un nuevo workspace en el proyecto actual"""
        if not self.current_project:
            return None

        # Crear workspace en el proyecto
        workspace = self.current_project.create_workspace("New Workspace")

        # Actualizar UI
        self.workspace_tree.set_project(self.current_project)

        return workspace

    def create_room(self, workspace_id: str) -> Room:
        """Crea una nueva room en el workspace especificado"""
        if not self.current_project or workspace_id not in self.current_project.workspaces:
            return None

        workspace = self.current_project.workspaces[workspace_id]
        room = workspace.create_room("New Room")

        # Actualizar UI
        self.workspace_tree.set_project(self.current_project)

        return room

    def rename_workspace(self, workspace_id: str, new_name: str):
        """Renombra un workspace"""
        if self.current_project and workspace_id in self.current_project.workspaces:
            workspace = self.current_project.workspaces[workspace_id]
            workspace.name = new_name
            self.workspace_tree.set_project(self.current_project)

    def rename_room(self, workspace_id: str, room_id: str, new_name: str):
        """Renombra una room"""
        if (self.current_project and
                workspace_id in self.current_project.workspaces and
                room_id in self.current_project.workspaces[workspace_id].rooms):
            room = self.current_project.workspaces[workspace_id].rooms[room_id]
            room.name = new_name
            self.workspace_tree.set_project(self.current_project)

    def delete_workspace(self, workspace_id: str):
        """Elimina un workspace y todas sus rooms"""
        if self.current_project and workspace_id in self.current_project.workspaces:
            del self.current_project.workspaces[workspace_id]
            self.workspace_tree.set_project(self.current_project)

    def delete_room(self, workspace_id: str, room_id: str):
        """Elimina una room"""
        if (self.current_project and
                workspace_id in self.current_project.workspaces and
                room_id in self.current_project.workspaces[workspace_id].rooms):
            del self.current_project.workspaces[workspace_id].rooms[room_id]
            self.workspace_tree.set_project(self.current_project)