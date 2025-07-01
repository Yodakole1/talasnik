from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

class SmartTimeEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(5)  # HH:MM
        self.textChanged.connect(self._auto_colon)

    def _auto_colon(self, text):
        # Only insert colon if not already present and length is 2
        if len(text) == 2 and ':' not in text:
            self.setText(text + ':')
            self.setCursorPosition(3)
        # Optionally, restrict to digits and colon
        elif len(text) > 0:
            filtered = ''.join([c for c in text if c.isdigit() or c == ':'])
            if filtered != text:
                self.setText(filtered)

class TimeDelegate(QStyledItemDelegate):
    """Delegate to only allow HH:MM 24-hour time format in the Time column, with auto-colon."""
    def createEditor(self, parent, option, index):
        editor = SmartTimeEdit(parent)
        regex = QRegExp(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
        validator = QRegExpValidator(regex, editor)
        editor.setValidator(validator)
        editor.setPlaceholderText("HH:MM")
        return editor

class LettersOnlyDelegate(QStyledItemDelegate):
    """Delegate to only allow letters (and optionally spaces) in a cell."""
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        regex = QRegExp(r"^[A-Za-z\s]+$")
        validator = QRegExpValidator(regex, editor)
        editor.setValidator(validator)
        editor.setPlaceholderText("Letters only")
        return editor