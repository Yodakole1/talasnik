from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

class TimeDelegate(QStyledItemDelegate):
    """Delegate to only allow HH:MM 24-hour time format in the Time column."""
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
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