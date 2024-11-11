from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeWidget,
                               QTreeWidgetItem, QPushButton, QMenu, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from .base_panel import BasePanel


class WorkspaceTree(QTreeWidget):
    """Tree widget for displaying workspaces and rooms"""
    roomSelected = Signal(str, str)

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

    def create_workspace(self):
        workspace = QTreeWidgetItem(self)
        workspace.setText(0, "🗀 New Workspace")
        workspace.setExpanded(True)
        self.editItem(workspace)

    def create_room(self, workspace_item):
        room = QTreeWidgetItem(workspace_item)
        room.setText(0, "└ New Room")
        workspace_item.setExpanded(True)
        self.editItem(room)

    def rename_item(self, item):
        self.editItem(item)

    def delete_workspace(self, workspace_item):
        self.takeTopLevelItem(self.indexOfTopLevelItem(workspace_item))

    def delete_room(self, room_item):
        workspace_item = room_item.parent()
        workspace_item.removeChild(room_item)


class WorkspacePanel(BasePanel):
    def __init__(self):
        super().__init__("Workspaces")
        self.init_panel()

    def init_panel(self):
        # Workspace tree
        self.workspace_tree = WorkspaceTree()
        self.content_layout.addWidget(self.workspace_tree)

        # Set content margins
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(0)

        # Add example items
        project1 = QTreeWidgetItem(self.workspace_tree)
        project1.setText(0, "🗀 Dungeon Project")
        project1.setExpanded(True)

        room1 = QTreeWidgetItem(project1)
        room1.setText(0, "└ Room: Main Hall")

        room2 = QTreeWidgetItem(project1)
        room2.setText(0, "└ Room: Treasury")

        project2 = QTreeWidgetItem(self.workspace_tree)
        project2.setText(0, "🗀 Castle Project")