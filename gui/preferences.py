from PyQt5.QtWidgets import QDialog, QFormLayout, QCheckBox, QSpinBox, QFontComboBox, QHBoxLayout, QPushButton, QComboBox, QLabel
from PyQt5.QtGui import QFont

class PreferencesDialog(QDialog):
    def __init__(self, prefs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.prefs = prefs.copy()
        layout = QFormLayout(self)

        # General section
        general_label = QLabel("<b>General</b>")
        layout.addRow(general_label)

        self.dark_mode = QCheckBox("Enable high contrast dark mode")
        self.dark_mode.setChecked(self.prefs["dark_mode"])
        layout.addRow(self.dark_mode)

        self.rows = QSpinBox()
        self.rows.setRange(5, 100)
        self.rows.setValue(self.prefs["rows"])
        layout.addRow("Starting rows:", self.rows)

        self.font_family = QFontComboBox()
        self.font_family.setCurrentFont(QFont(self.prefs["font_family"]))
        layout.addRow("Font:", self.font_family)

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 32)
        self.font_size.setValue(self.prefs["font_size"])
        layout.addRow("Font size:", self.font_size)

        # Morse section
        morse_label = QLabel("<b>Morse</b>")
        layout.addRow(morse_label)

        self.morse_mode = QComboBox()
        self.morse_mode.addItems(["Spacebar (short/long)", "Mouse (left/right click)"])
        current_mode = self.prefs.get("morse_mode", "Spacebar (short/long)")
        idx = self.morse_mode.findText(current_mode)
        if idx >= 0:
            self.morse_mode.setCurrentIndex(idx)
        layout.addRow("Morse input mode:", self.morse_mode)

        self.show_morse_alphabet = QCheckBox("Show Morse alphabet in practicer")
        self.show_morse_alphabet.setChecked(self.prefs.get("show_morse_alphabet", False))
        layout.addRow(self.show_morse_alphabet)

        # Buttons
        btns = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addRow(btns)

        self.setLayout(layout)

        # Apply dark mode style if needed
        if self.prefs.get("dark_mode", False):
            self.setStyleSheet("""
                QDialog, QLabel, QCheckBox, QSpinBox, QFontComboBox, QPushButton {
                    color: white;
                    background-color: #222;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-size: 14pt;
                }
                QCheckBox::indicator {
                    width: 18px; height: 18px;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog, QLabel, QCheckBox, QSpinBox, QFontComboBox, QPushButton {
                    color: #23272e;
                    background-color: #f5f5f5;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-size: 14pt;
                }
                QCheckBox::indicator {
                    width: 18px; height: 18px;
                }
            """)

    def get_prefs(self):
        return {
            "dark_mode": self.dark_mode.isChecked(),
            "rows": self.rows.value(),
            "font_family": self.font_family.currentFont().family(),
            "font_size": self.font_size.value(),
            "morse_mode": self.morse_mode.currentText(),
            "show_morse_alphabet": self.show_morse_alphabet.isChecked()
        }