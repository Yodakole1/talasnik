from PyQt5.QtWidgets import QTableWidget, QHeaderView
from PyQt5.QtGui import QFont
from .delegates import TimeDelegate, LettersOnlyDelegate

class HamLogBook(QTableWidget):
    def __init__(self, rows, font_family, font_size, parent=None):
        super().__init__(rows, 4, parent)
        self.setHorizontalHeaderLabels(["Name", "Time", "Callsign", "Place"])
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.AllEditTriggers)
        self.setFont(QFont(font_family, font_size))
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
        self.setItemDelegateForColumn(2, letters_delegate)
        self.setItemDelegateForColumn(3, letters_delegate)