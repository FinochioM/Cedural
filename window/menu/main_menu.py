from PySide6.QtWidgets import QMenuBar, QMenu, QFileDialog
from PySide6.QtGui import QAction

class MainMenu(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_menu()

    def init_menu(self):
        # File Menu
        file_menu = QMenu("&File", self)

        new_action = QAction("New Project", self)
        open_action = QAction("Open Project", self)
        save_action = QAction("Save Project", self)
        save_as_action = QAction("Save Project As...", self)
        export_action = QAction("Export Room...", self)
        exit_action = QAction("Exit", self)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = QMenu("&Edit", self)

        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        preferences_action = QAction("Preferences", self)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(preferences_action)

        # View Menu
        view_menu = QMenu("&View", self)

        zoom_in_action = QAction("Zoom In", self)
        zoom_out_action = QAction("Zoom Out", self)
        reset_zoom_action = QAction("Reset Zoom", self)

        view_menu.addAction(zoom_in_action)
        view_menu.addAction(zoom_out_action)
        view_menu.addAction(reset_zoom_action)

        # Help Menu
        help_menu = QMenu("&Help", self)

        about_action = QAction("About", self)
        help_action = QAction("Help", self)

        help_menu.addAction(help_action)
        help_menu.addSeparator()
        help_menu.addAction(about_action)

        # Add all menus to the menubar
        self.addMenu(file_menu)
        self.addMenu(edit_menu)
        self.addMenu(view_menu)
        self.addMenu(help_menu)

        # Style the menu bar
        self.setStyleSheet("""
            QMenuBar {
                background-color: #2D2D2D;
                color: #CCCCCC;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3D3D3D;
            }
            QMenu {
                background-color: #2D2D2D;
                color: #CCCCCC;
                border: 1px solid #454545;
            }
            QMenu::item {
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background-color: #3D3D3D;
            }
            QMenu::separator {
                height: 1px;
                background-color: #454545;
                margin: 4px 0px;
            }
        """)