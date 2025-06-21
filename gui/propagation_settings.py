from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QLabel, QMessageBox

SOLAR_WIDGETS = [
    ("Solar N0NBH", "https://www.hamqsl.com/solarn0nbh.php"),
    ("Solar Pic", "https://www.hamqsl.com/solarpic.php"),
    ("Solar VHF", "https://www.hamqsl.com/solarvhf.php"),
    ("Solar", "https://www.hamqsl.com/solar.php"),
    ("Solar Small", "https://www.hamqsl.com/solarsmall.php"),
    ("Solar 2", "https://www.hamqsl.com/solar2.php"),
    ("Solar 101 Pic", "https://www.hamqsl.com/solar101pic.php"),
    ("Solar 101 VHF/Per", "https://www.hamqsl.com/solar101vhfper.php"),
    ("Solar 101 VHF Pic", "https://www.hamqsl.com/solar101vhfpic.php"),
    ("Solar 101 SC", "https://www.hamqsl.com/solar101sc.php"),
    ("Solar Graph", "https://www.hamqsl.com/solargraph.php"),
    ("Solar MUF", "https://www.hamqsl.com/solarmuf.php"),
]

class PropagationSettingsDialog(QDialog):
    def __init__(self, selected=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Propagation Settings")
        self.resize(400, 400)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select up to 3 solar widgets to display:"))
        self.checkboxes = []
        for name, url in SOLAR_WIDGETS:
            cb = QCheckBox(name)
            if selected and url in selected:
                cb.setChecked(True)
            cb.stateChanged.connect(self.limit_selection)
            self.checkboxes.append(cb)
            layout.addWidget(cb)
        self.info = QLabel("")
        layout.addWidget(self.info)
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        self.setLayout(layout)

        # Apply dark mode style if needed
        dark_mode = False
        if parent and hasattr(parent, "prefs"):
            dark_mode = parent.prefs.get("dark_mode", False)
        if dark_mode:
            self.setStyleSheet("""
                QDialog, QLabel, QCheckBox, QPushButton {
                    color: white;
                    background-color: #222;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-size: 15pt;
                    font-weight: 500;
                }
                QPushButton {
                    border: 1px solid #555;
                    border-radius: 12px;
                }
                QCheckBox::indicator {
                    width: 18px; height: 18px;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog, QLabel, QCheckBox, QPushButton {
                    color: #23272e;
                    background-color: #f5f5f5;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-size: 15pt;
                    font-weight: 500;
                }
                QPushButton {
                    border: 1px solid #bbb;
                    border-radius: 12px;
                }
                QCheckBox::indicator {
                    width: 18px; height: 18px;
                }
            """)

    def limit_selection(self):
        checked = [cb for cb in self.checkboxes if cb.isChecked()]
        if len(checked) > 3:
            self.info.setText("You can select up to 3 widgets.")
            # Uncheck the last one checked
            sender = self.sender()
            sender.setChecked(False)
        else:
            self.info.setText("")

    def get_selected_urls(self):
        return [url for cb, (name, url) in zip(self.checkboxes, SOLAR_WIDGETS) if cb.isChecked()]