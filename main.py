from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
import sys
from window.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    app.setStyle('Fusion')
    apply_dark_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

def apply_dark_theme(app):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1E1E1E"))
    palette.setColor(QPalette.WindowText, QColor("#CCCCCC"))
    palette.setColor(QPalette.Base, QColor("#252526"))
    palette.setColor(QPalette.AlternateBase, QColor("#2D2D2D"))
    palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(QPalette.ToolTipText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Text, QColor("#CCCCCC"))
    palette.setColor(QPalette.Button, QColor("#252526"))
    palette.setColor(QPalette.ButtonText, QColor("#CCCCCC"))
    palette.setColor(QPalette.BrightText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Highlight, QColor("#264F78"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))

    app.setPalette(palette)

    # Estilo adicional para widgets específicos
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1E1E1E;
        }
        QPushButton {
            background-color: #264F78;
            border: none;
            border-radius: 5px;
            padding: 5px 15px;
            color: white;
        }
        QPushButton:hover {
            background-color: #365F88;
        }
        QPushButton#generateButton {
            background-color: #2C7A3D;
        }
        QPushButton#generateButton:hover {
            background-color: #3C8A4D;
        }
        QSplitter::handle {
            background-color: #353535;
        }
        QHeaderView::section {
            background-color: #2D2D2D;
            color: #CCCCCC;
            padding: 5px;
            border: none;
        }
    """)


if __name__ == "__main__":
    main()