from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTextEdit, QLabel, QMessageBox, QWidget)
from PySide6.QtGui import (QSyntaxHighlighter, QTextCharFormat, QColor,
                           QFont, QTextCursor)
from PySide6.QtCore import Qt, QRegularExpression
import json


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Resaltador de sintaxis para JSON"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Formato para strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append(
            (QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'), string_format)
        )

        # Formato para números
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append(
            (QRegularExpression(r'\b\d+\.?\d*\b'), number_format)
        )

        # Formato para palabras clave
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keywords = ["true", "false", "null"]
        for word in keywords:
            self.highlighting_rules.append(
                (QRegularExpression(f"\\b{word}\\b"), keyword_format)
            )

        # Formato para llaves y corchetes
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor("#D4D4D4"))
        self.highlighting_rules.append(
            (QRegularExpression("[\{\}\[\]]"), bracket_format)
        )

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class JsonEditor(QTextEdit):
    """Editor de texto con funcionalidades específicas para JSON"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #454545;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)

        # Configurar la fuente
        font = QFont("Consolas", 12)
        font.setFixedPitch(True)
        self.setFont(font)

        # Agregar el resaltador de sintaxis
        self.highlighter = JsonSyntaxHighlighter(self.document())

    def format_json(self):
        """Formatea el JSON con indentación adecuada"""
        try:
            text = self.toPlainText()
            if text.strip():
                parsed = json.loads(text)
                formatted = json.dumps(parsed, indent=2)
                self.setPlainText(formatted)
                return True
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "JSON Error", f"Invalid JSON: {str(e)}")
            return False
        return True

    def auto_indent(self):
        """Auto-indenta el texto cuando se presiona Enter"""
        cursor = self.textCursor()
        text = cursor.block().text()
        indent = ''

        # Contar espacios al inicio de la línea actual
        for char in text:
            if char == ' ':
                indent += ' '
            else:
                break

        # Agregar indentación adicional si la línea termina con {
        if text.strip().endswith('{') or text.strip().endswith('['):
            indent += '  '

        cursor.insertText('\n' + indent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.auto_indent()
        else:
            super().keyPressEvent(event)


class JsonEditorDialog(QDialog):
    def __init__(self, json_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JSON Editor")
        self.resize(800, 600)
        self.init_ui()
        if json_data:
            self.set_json(json_data)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        # Botón de formato
        format_button = QPushButton("Format JSON")
        format_button.clicked.connect(self.format_json)
        format_button.setStyleSheet("""
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
        """)

        toolbar.addWidget(format_button)
        toolbar.addStretch()

        # Editor
        self.editor = JsonEditor()

        # Botones de acción
        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        for button in [save_button, cancel_button]:
            button.setStyleSheet("""
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
            """)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        # Agregar widgets al layout principal
        layout.addLayout(toolbar)
        layout.addWidget(self.editor)
        layout.addLayout(button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
        """)

    def set_json(self, json_data):
        """Establece el contenido JSON en el editor"""
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                pass
        formatted_json = json.dumps(json_data, indent=2)
        self.editor.setPlainText(formatted_json)

    def get_json(self):
        """Obtiene el JSON del editor"""
        try:
            return json.loads(self.editor.toPlainText())
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "JSON Error", f"Invalid JSON: {str(e)}")
            return None

    def format_json(self):
        """Formatea el JSON actual"""
        self.editor.format_json()