from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QKeyEvent
from PyQt5.QtCore import Qt, QRegExp

class CodeEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText(" " * 4)  # 4 boşluk
        elif event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                parent = self.parent()
                if hasattr(parent, "change_font_size"):
                    parent.change_font_size(120)
            elif event.key() == Qt.Key_Minus:
                parent = self.parent()
                if hasattr(parent, "change_font_size"):
                    parent.change_font_size(-120)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            parent = self.parent()
            if hasattr(parent, "change_font_size"):
                parent.change_font_size(delta)
            event.accept()
        else:
            super().wheelEvent(event)

class ArduinoSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Anahtar kelimeler
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "void", "int", "float", "long", "bool", "char", "if", "else", "for", "while",
            "HIGH", "LOW", "INPUT", "OUTPUT", "true", "false", "return"
        ]
        for word in keywords:
            pattern = QRegExp(rf"\b{word}\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Fonksiyon isimleri
        func_format = QTextCharFormat()
        func_format.setForeground(QColor("#DCDCAA"))
        functions = ["pinMode", "digitalWrite", "digitalRead", "analogRead", "analogWrite", "delay"]
        for func in functions:
            pattern = QRegExp(rf"\b{func}(?=\s*\()")
            self.highlighting_rules.append((pattern, func_format))

        # Yorumlar
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_pattern = QRegExp("//[^\n]*")
        self.highlighting_rules.append((comment_pattern, comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            i = pattern.indexIn(text, 0)
            while i >= 0:
                length = pattern.matchedLength()
                self.setFormat(i, length, fmt)
                i = pattern.indexIn(text, i + length)


class ArduinoCodeEditorWindow(QDialog):
    def __init__(self, arduino_component):
        super().__init__()
        self.arduino = arduino_component
        self.setWindowTitle(f"Arduino Kod Editörü - {self.arduino.unique_id[:8]}")
        self.resize(600, 500)
        
        self.font_size = 12

        layout = QVBoxLayout()
        self.editor = CodeEditor()
        self.editor.setFont(QFont("Courier", self.font_size))
        self.editor.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.highlighter = ArduinoSyntaxHighlighter(self.editor.document())

        if not self.arduino.code.strip():
            self.arduino.code = (
                "// Arduino kodunuzu buraya yazın\n\n"
                "void setup() {\n"
                "    // Başlatma kodları\n"
                "}\n\n"
                "void loop() {\n"
                "    // Sürekli çalışan kodlar\n"
                "}\n"
            )

        self.editor.setText(self.arduino.code)
        self.editor.textChanged.connect(self.save_code_to_component)

        layout.addWidget(self.editor)
        self.setLayout(layout)

    def save_code_to_component(self):
        self.arduino.code = self.editor.toPlainText()
        
    def change_font_size(self, delta):
        if delta > 0 and self.font_size < 32:
            self.font_size += 1
        elif delta < 0 and self.font_size > 6:
            self.font_size -= 1
        self.editor.setFont(QFont("Courier", self.font_size))