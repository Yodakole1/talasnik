import os
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QLineEdit, QPushButton, QProgressBar, QMessageBox, QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal

class UploadThread(QThread):
    finished = pyqtSignal(bool, str)
    def __init__(self, port, in_file, upload_func):
        super().__init__()
        self.port = port
        self.in_file = in_file
        self.upload_func = upload_func
    def run(self):
        try:
            self.upload_func(self.port, self.in_file)
            self.finished.emit(True, f"✅ Upload complete: {self.in_file}")
        except Exception as e:
            self.finished.emit(False, f"❌ Upload failed: {e}")

class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upload Radio Memory")
        layout = QFormLayout(self)
        self.radio_type_combo = QComboBox()
        self.radio_type_combo.addItems(["Baofeng UV-5R"])
        layout.addRow("Radio type:", self.radio_type_combo)
        from serial.tools import list_ports
        self.port_combo = QComboBox()
        self.port_combo.addItems([p.device for p in list_ports.comports()])
        layout.addRow("Serial port:", self.port_combo)

        # File selection with browse button
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("radio.img")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)
        layout.addRow("Image file:", file_layout)

        self.upload_btn = QPushButton("Upload")
        self.upload_btn.clicked.connect(self.on_upload)
        layout.addRow(self.upload_btn)
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
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QProgressBar {
                    color: #222;
                    background-color: #f5f5f5;
                }
                QLineEdit, QComboBox {
                    border: 1px solid #bbb;
                }
                QPushButton {
                    border: 1px solid #bbb;
                }
            """)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.img);;All Files (*)"
        )
        if path:
            self.file_edit.setText(path)

    def on_upload(self):
        port = self.port_combo.currentText()
        radio_type = self.radio_type_combo.currentText()
        in_file = self.file_edit.text().strip()
        if not in_file or not os.path.isfile(in_file):
            QMessageBox.warning(self, "Input Error", "Please select a valid image file.")
            return
        self.progress.show()
        self.upload_btn.setEnabled(False)
        from radio.uv5r import upload_radio as upload_radio_uv5r
        upload_func = upload_radio_uv5r
        self.thread = UploadThread(port, in_file, upload_func)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, success, msg):
        self.progress.hide()
        self.upload_btn.setEnabled(True)
        if self.parent() and hasattr(self.parent(), "show_message"):
            self.parent().show_message("Upload Result", msg)
        else:
            QMessageBox.information(self, "Upload Result", msg)
        self.accept()