from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .delegates import TimeDelegate, LettersOnlyDelegate

class HamLogBook(QTableWidget):
    def __init__(self, rows, font_family, font_size, parent=None):
        super().__init__(rows, 4, parent)  # <-- Only 4 columns!
        self.setHorizontalHeaderLabels(["Name", "Time", "Callsign", "Place"])
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.AllEditTriggers)
        self.setFontFamily(font_family)
        self.setFontSize(font_size)
        self.setStyleSheet(f"""
            QTableWidget {{
                font-size: {font_size + 2}px;
                border-radius: 8px;
                background: #23272e if self.prefs.get("dark_mode") else "#fff;
            }}
            QHeaderView::section {{
                padding: 8px;
                font-weight: bold;
                border-radius: 8px;
            }}
        """)
        self.setSortingEnabled(True)
        self.setItemDelegateForColumn(1, TimeDelegate(self))
        letters_delegate = LettersOnlyDelegate(self)
        self.setItemDelegateForColumn(0, letters_delegate)
        self.setItemDelegateForColumn(3, letters_delegate)
        self.undo_stack = []
        self.redo_stack = []
        self.last_edit = None
        self.cellChanged.connect(self.handle_cell_changed)

    def setFontFamily(self, family):
        font = self.font()
        font.setFamily(family)
        self.setFont(font)

    def setFontSize(self, size):
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def handle_cell_changed(self, row, col):
        if self.last_edit is not None:
            # Prevent recursion
            return
        item = self.item(row, col)
        if item:
            old_value = getattr(item, "_old_value", "")
            new_value = item.text()
            if old_value != new_value:
                self.undo_stack.append((row, col, old_value, new_value))
                self.redo_stack.clear()
            item._old_value = new_value

    def editItem(self, item):
        # Store old value before editing
        item._old_value = item.text()
        super().editItem(item)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z:
            self.undo()
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Y:
            self.redo()
        else:
            super().keyPressEvent(event)

    def undo(self):
        if not self.undo_stack:
            return
        row, col, old_value, new_value = self.undo_stack.pop()
        item = self.item(row, col)
        if item:
            self.last_edit = True
            item.setText(old_value)
            self.last_edit = None
            self.redo_stack.append((row, col, old_value, new_value))

    def redo(self):
        if not self.redo_stack:
            return
        row, col, old_value, new_value = self.redo_stack.pop()
        item = self.item(row, col)
        if item:
            self.last_edit = True
            item.setText(new_value)
            self.last_edit = None
            self.undo_stack.append((row, col, old_value, new_value))