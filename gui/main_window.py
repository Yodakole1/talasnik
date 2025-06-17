import os
import json
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QVBoxLayout, QWidget, QLabel, QFileDialog, QMessageBox, QTableWidgetItem, QHBoxLayout, QPushButton, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPalette, QColor
from .hamlog import HamLogBook
from .preferences import PreferencesDialog
from .antenna_calc import AntennaCalculatorDialog
from .dump_dialog import DumpDialog
from .propagation_info import PropagationInfoDialog
from .upload_dialog import UploadDialog
from .propagation_settings import PropagationSettingsDialog
from .morse_practicer import MorsePracticerDialog
from .morse_translator import MorseTranslatorDialog

PREFS_FILE = "talasnik_prefs.json"
DEFAULT_PREFS = {
    "dark_mode": False,
    "rows": 20,
    "font_family": "Arial",
    "font_size": 15,
    "solar_widgets": [
        "https://www.hamqsl.com/solar101vhfper.php"
    ]
}

def load_prefs():
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, "r") as f:
            return {**DEFAULT_PREFS, **json.load(f)}
    return DEFAULT_PREFS.copy()

def save_prefs(prefs):
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f)

def show_dark_messagebox(parent, title, text, icon=QMessageBox.Information):
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setIcon(icon)
    palette = box.palette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.WindowText, Qt.white)
    box.setPalette(palette)
    box.setStyleSheet("QLabel{color:white;} QPushButton{color:white; background-color:#444;}")
    box.exec_()

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Talasnik")
        self.setFixedSize(400, 220)
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        label = QLabel(
            "<b style='font-size:22px;'>Talasnik</b><br>"
            "<span style='font-size:15px;'>by Yodakole1</span><br>"
            "<a href='https://github.com/Yodakole1' style='font-size:14px;'>github.com/Yodakole1</a><br>"
            "<span style='font-size:13px;'>&copy; 2025</span>"
        )
        label.setOpenExternalLinks(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        btn = QPushButton("OK")
        btn.setFixedWidth(90)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        # Style for dark/light mode
        dark_mode = False
        if parent and hasattr(parent, "prefs"):
            dark_mode = parent.prefs.get("dark_mode", False)
        if dark_mode:
            self.setStyleSheet("""
                QDialog {
                    background: #23272e;
                }
                QLabel {
                    color: white;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-weight: 500;
                }
                QPushButton {
                    color: white;
                    background: #23272e;
                    border: 1px solid #555;
                    border-radius: 12px;
                    font-size: 14pt;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                }
                QPushButton:hover {
                    background: #3a3f4b;
                }
                QPushButton:pressed {
                    background: #0078d7;
                }
                a { color: #4fc3f7; }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background: #f5f5f5;
                }
                QLabel {
                    color: #23272e;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-weight: 500;
                }
                QPushButton {
                    color: #23272e;
                    background: #f5f5f5;
                    border: 1px solid #bbb;
                    border-radius: 12px;
                    font-size: 14pt;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                }
                QPushButton:hover {
                    background: #e0e0e0;
                }
                QPushButton:pressed {
                    background: #0078d7;
                    color: #fff;
                }
                a { color: #1976d2; }
            """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.prefs = load_prefs()
        self.setWindowTitle("Talasnik - Ham Log Book")
        self.resize(800, 500)
        self.setStyle()
        self.init_menu()
        self.init_ui()
        self.add_custom_titlebar()

    def setStyle(self):
        if self.prefs["dark_mode"]:
            self.set_dark_palette()
        else:
            self.set_light_palette()

    def set_dark_palette(self):
        QApplication.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.Base, QColor(20, 20, 20))
        palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        QApplication.setPalette(palette)

    def set_light_palette(self):
        QApplication.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(235, 235, 235))
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(220, 220, 220))
        QApplication.setPalette(palette)

    def init_menu(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Settings")
        tools_menu = menubar.addMenu("Tools")
        export_menu = menubar.addMenu("Export")
        import_menu = menubar.addMenu("Import")
        propagation_info_menu = menubar.addMenu("Propagation Info")

        pref_action = QAction("Preferences...", self)
        pref_action.triggered.connect(self.open_preferences)
        settings_menu.addAction(pref_action)

        dump_action = QAction("Dump Radio Memory...", self)
        dump_action.triggered.connect(self.open_dump_dialog)
        tools_menu.addAction(dump_action)

        upload_action = QAction("Upload Radio Memory...", self)
        upload_action.triggered.connect(self.open_upload_dialog)
        tools_menu.addAction(upload_action)

        calc_action = QAction("Antenna Calculator...", self)
        calc_action.triggered.connect(self.open_calc_dialog)
        tools_menu.addAction(calc_action)

        morse_action = QAction("Morse Code Practicer...", self)
        morse_action.triggered.connect(self.open_morse_practicer)
        tools_menu.addAction(morse_action)

        morse_translator_action = QAction("Morse Code Translator...", self)
        morse_translator_action.triggered.connect(self.open_morse_translator)
        tools_menu.addAction(morse_translator_action)

        export_action = QAction("Export Log...", self)
        export_action.triggered.connect(self.export_log)
        export_menu.addAction(export_action)

        import_action = QAction("Import Log...", self)
        import_action.triggered.connect(self.import_log)
        import_menu.addAction(import_action)

        propagation_info_action = QAction("Show Propagation Info...", self)
        propagation_info_action.triggered.connect(self.open_propagation_info)
        propagation_info_menu.addAction(propagation_info_action)

        propagation_settings_action = QAction("Propagation Settings...", self)
        propagation_settings_action.triggered.connect(self.open_propagation_settings)
        propagation_info_menu.addAction(propagation_settings_action)

        about_menu = menubar.addMenu("About")
        about_action = QAction("About Talasnik", self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        welcome = QLabel("Welcome to Talasnik\nHam Log Book below:")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        self.logbook = HamLogBook(
            self.prefs["rows"],
            self.prefs["font_family"],
            self.prefs["font_size"]
        )
        layout.addWidget(self.logbook)
        central.setLayout(layout)
        self.setCentralWidget(central)

        color = "#23272e" if not self.prefs.get("dark_mode") else "white"
        welcome.setStyleSheet(
            f"font-family: 'Segoe UI', 'Arial', sans-serif; font-size: 22px; font-weight: 600; margin-bottom: 12px; color: {color} !important;"
        )

    def add_custom_titlebar(self):
        titlebar = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 8, 8, 0)
        layout.setSpacing(8)

        # Minimize button
        btn_min = QPushButton("–")
        btn_min.setFixedSize(36, 36)
        btn_min.setCursor(Qt.PointingHandCursor)
        btn_min.clicked.connect(self.showMinimized)
        # Maximize/Restore button
        btn_max = QPushButton("▢")
        btn_max.setFixedSize(36, 36)
        btn_max.setCursor(Qt.PointingHandCursor)
        btn_max.clicked.connect(self.toggle_fullscreen)
        btn_max.setFont(QFont("DejaVu Sans Mono", 18, QFont.Bold))
        btn_max.setStyleSheet(btn_max.styleSheet() + "padding-bottom: 2px;")
        # Close button
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(36, 36)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.close)

        # Modern style
        btn_style_dark = """
            QPushButton {
                background: #23272e; color: #fff; border: none; border-radius: 18px;
                font-size: 18pt; font-weight: bold;
            }
            QPushButton:hover {
                background: #3a3f4b;
            }
            QPushButton:pressed {
                background: #0078d7;
            }
        """
        btn_style_light = """
            QPushButton {
                background: #f5f5f5; color: #23272e; border: none; border-radius: 18px;
                font-size: 18pt; font-weight: bold;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
            QPushButton:pressed {
                background: #0078d7; color: #fff;
            }
        """
        style = btn_style_dark if self.prefs.get("dark_mode") else btn_style_light
        for btn in (btn_min, btn_max, btn_close):
            btn.setStyleSheet(style)

        layout.addWidget(btn_min)
        layout.addWidget(btn_max)
        layout.addWidget(btn_close)
        titlebar.setLayout(layout)

        # Add to the main layout at the top right
        central = self.centralWidget()
        if central is not None:
            main_layout = central.layout()
            if main_layout is not None:
                main_layout.insertWidget(0, titlebar, alignment=Qt.AlignRight | Qt.AlignTop)
        self._is_fullscreen = True

    def toggle_fullscreen(self):
        if self._is_fullscreen:
            self.showNormal()
            self._is_fullscreen = False
        else:
            self.showFullScreen()
            self._is_fullscreen = True

    def open_preferences(self):
        dlg = PreferencesDialog(self.prefs, self)
        if dlg.exec_():
            self.prefs = dlg.get_prefs()
            save_prefs(self.prefs)
            self.setStyle()
            # --- Save current data ---
            old_data = []
            for row in range(self.logbook.rowCount()):
                row_data = []
                for col in range(self.logbook.columnCount()):
                    item = self.logbook.item(row, col)
                    row_data.append(item.text() if item else "")
                old_data.append(row_data)
            columns = [self.logbook.horizontalHeaderItem(i).text() for i in range(self.logbook.columnCount())]
            # --- Rebuild logbook with new settings ---
            self.centralWidget().layout().removeWidget(self.logbook)
            self.logbook.deleteLater()
            self.logbook = HamLogBook(
                self.prefs["rows"],
                self.prefs["font_family"],
                self.prefs["font_size"]
            )
            self.centralWidget().layout().addWidget(self.logbook)
            # --- Restore data (truncate or pad as needed) ---
            for row_idx, row_data in enumerate(old_data):
                if row_idx >= self.logbook.rowCount():
                    self.logbook.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    if col_idx < self.logbook.columnCount():
                        item = QTableWidgetItem(value)
                        if self.prefs.get("dark_mode"):
                            item.setForeground(QColor(Qt.white))
                        self.logbook.setItem(row_idx, col_idx, item)

    def open_dump_dialog(self):
        dlg = DumpDialog(self)
        dlg.exec_()

    def open_upload_dialog(self):
        dlg = UploadDialog(self)
        dlg.exec_()

    def open_calc_dialog(self):
        dlg = AntennaCalculatorDialog(self, dark_mode=self.prefs.get("dark_mode", False))
        dlg.exec_()

    def open_morse_practicer(self):
        dlg = MorsePracticerDialog(self.prefs.get("morse_mode", "Spacebar (short/long)"), self)
        dlg.exec_()

    def open_morse_translator(self):
        dlg = MorseTranslatorDialog(self)
        dlg.exec_()

    def export_log(self):
        options = QFileDialog.Options()
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            "",
            "Excel Files (*.xlsx);;JSON Files (*.json)",
            options=options
        )
        if not path:
            return

        # Add extension if missing
        if selected_filter.startswith("Excel") and not path.lower().endswith(".xlsx"):
            path += ".xlsx"
        elif selected_filter.startswith("JSON") and not path.lower().endswith(".json"):
            path += ".json"

        # Gather data from table
        data = []
        for row in range(self.logbook.rowCount()):
            row_data = []
            for col in range(self.logbook.columnCount()):
                item = self.logbook.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        columns = [self.logbook.horizontalHeaderItem(i).text() for i in range(self.logbook.columnCount())]
        df = pd.DataFrame(data, columns=columns)
        if path.endswith(".xlsx"):
            df.to_excel(path, index=False)
        else:
            df.to_json(path, orient="records", indent=2)

    def import_log(self):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Log",
            "",
            "Excel Files (*.xlsx);;JSON Files (*.json)",
            options=options
        )
        if not path:
            return

        try:
            if path.endswith(".xlsx"):
                df = pd.read_excel(path)
            else:
                df = pd.read_json(path)
            # Clear current table
            self.logbook.setRowCount(0)
            self.logbook.setColumnCount(len(df.columns))
            self.logbook.setHorizontalHeaderLabels([str(col) for col in df.columns])
            # Fill table with imported data
            for row_idx, row in df.iterrows():
                self.logbook.insertRow(row_idx)
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    if self.prefs.get("dark_mode"):
                        item.setForeground(QColor(Qt.white))
                    self.logbook.setItem(row_idx, col_idx, item)
            QMessageBox.information(self, "Import", f"Imported {len(df)} rows from: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import: {e}")

    def show_message(self, title, msg):
        if self.prefs.get("dark_mode"):
            show_dark_messagebox(self, title, msg)
        else:
            box = QMessageBox(self)
            box.setWindowTitle(title)
            box.setText(msg)
            box.exec_()

    def open_propagation_info(self):
        dlg = PropagationInfoDialog(self)
        dlg.exec_()

    def open_propagation_settings(self):
        dlg = PropagationSettingsDialog(self.prefs.get("solar_widgets", []), self)
        if dlg.exec_():
            self.prefs["solar_widgets"] = dlg.get_selected_urls()
            save_prefs(self.prefs)

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec_()