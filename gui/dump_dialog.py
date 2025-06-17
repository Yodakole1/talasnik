import random
import string
import serial
import serial.tools.list_ports
import time
import os
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QLineEdit, QPushButton, QProgressBar, QMessageBox, QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal

class DumpThread(QThread):
    finished = pyqtSignal(bool, str)
    def __init__(self, port, out_file, dump_func):
        super().__init__()
        self.port = port
        self.out_file = out_file
        self.dump_func = dump_func
    def run(self):
        try:
            self.ser = serial.Serial(self.port, 9600, timeout=1)
            self.ser.setDTR(True)
            self.ser.setRTS(True)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            time.sleep(0.5)
            self.dump_func(self.port, self.out_file)
            self.finished.emit(True, f"✅ Dump complete: {self.out_file}")
        except Exception as e:
            self.finished.emit(False, f"❌ Dump failed: {e}")

class DumpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dump Radio Memory")
        layout = QFormLayout(self)
        self.radio_type_combo = QComboBox()
        self.radio_type_combo.addItems(["Baofeng UV-5R"])
        layout.addRow("Radio type:", self.radio_type_combo)
        self.port_combo = QComboBox()
        self.port_combo.addItems([p.device for p in serial.tools.list_ports.comports()])
        layout.addRow("Serial port:", self.port_combo)

        # File selection with browse button
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("radio.img (leave blank for random)")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)
        layout.addRow("Image file:", file_layout)

        self.ready_btn = QPushButton("Ready")
        self.ready_btn.clicked.connect(self.on_ready)
        layout.addRow(self.ready_btn)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addRow(self.progress)
        self.resize(420, 180)

        # Apply dark mode style if needed
        dark_mode = False
        if parent and hasattr(parent, "prefs"):
            dark_mode = parent.prefs.get("dark_mode", False)
        if dark_mode:
            self.setStyleSheet("""
                QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QProgressBar {
                    color: white;
                    background-color: #222;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-size: 15pt;
                    font-weight: 500;
                }
                QLineEdit, QComboBox {
                    border: 1px solid #555;
                }
                QPushButton {
                    border: 1px solid #555;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QProgressBar {
                    color: #222;
                    background-color: #f5f5f5;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-size: 15pt;
                    font-weight: 500;
                }
                QLineEdit, QComboBox {
                    border: 1px solid #bbb;
                }
                QPushButton {
                    border: 1px solid #bbb;
                }
            """)

    def browse_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Dump File",
            "",
            "Image Files (*.img);;All Files (*)"
        )
        if path:
            if not path.lower().endswith('.img'):
                path += '.img'
            self.file_edit.setText(path)

    def on_ready(self):
        port = self.port_combo.currentText()
        radio_type = self.radio_type_combo.currentText()
        out_file = self.file_edit.text().strip()
        if not out_file:
            rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            out_file = os.path.join(os.path.expanduser("~"), f"radio_{rand}.img")
        self.progress.show()
        self.ready_btn.setEnabled(False)
        from radio.uv5r import dump_radio as dump_radio_uv5r
        dump_func = dump_radio_uv5r
        self.thread = DumpThread(port, out_file, dump_func)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, success, msg):
        self.progress.hide()
        self.ready_btn.setEnabled(True)
        if self.parent() and hasattr(self.parent(), "show_message"):
            self.parent().show_message("Dump Result", msg)
        else:
            QMessageBox.information(self, "Dump Result", msg)
        self.accept()