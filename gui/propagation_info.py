import tempfile
import folium
import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox, QSizePolicy, QHBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer, Qt
from PyQt5.QtGui import QPalette, QColor

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

class PropagationMapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Area Propagation Map (Real-Time)")
        self.resize(800, 600)
        layout = QVBoxLayout(self)

        self.band_combo = QComboBox()
        self.band_combo.addItems([
            "20m", "40m", "80m", "15m", "10m", "6m", "2m"
        ])
        band_label = QLabel("Band:")
        layout.addWidget(band_label)
        layout.addWidget(self.band_combo)

        self.refresh_btn = QPushButton("Refresh Map")
        self.refresh_btn.clicked.connect(self.update_map)
        layout.addWidget(self.refresh_btn)

        self.indices_label = QLabel()
        self.indices_label.setWordWrap(True)
        layout.addWidget(self.indices_label)

        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.close)
        layout.addWidget(self.back_btn)

        self.webview = QWebEngineView()
        layout.addWidget(self.webview, stretch=1)

        self.setLayout(layout)

        # Detect dark mode from parent if possible
        dark_mode = False
        if parent and hasattr(parent, "prefs"):
            dark_mode = parent.prefs.get("dark_mode", False)
        self.apply_style(dark_mode)
        self.update_map()
        self.update_indices_panel()

    def apply_style(self, dark_mode):
        if dark_mode:
            self.setStyleSheet("""
                QDialog {
                    background: #23272e;
                }
                QPushButton {
                    color: #fff;
                    background: #23272e;
                    font-size: 15pt;
                    border: none;
                    border-radius: 18px;
                    padding: 8px 24px;
                    margin: 8px 0;
                }
                QPushButton:hover {
                    background: #3a3f4b;
                }
                QPushButton:pressed {
                    background: #0078d7;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background: #f5f5f5;
                }
                QPushButton {
                    color: #23272e;
                    background: #f5f5f5;
                    font-size: 15pt;
                    border: none;
                    border-radius: 18px;
                    padding: 8px 24px;
                    margin: 8px 0;
                }
                QPushButton:hover {
                    background: #e0e0e0;
                }
                QPushButton:pressed {
                    background: #0078d7;
                    color: #fff;
                }
            """)

    
    def fetch_propagation_indices(self):
        url = "https://www.hamqsl.com/solarjson.php"
        try:
            r = requests.get(url, timeout=10)
            data = r.json().get("solar", {})
            return data
        except Exception as e:
            return {"error": str(e)}

    def update_indices_panel(self):
        data = self.fetch_propagation_indices()
        if "error" in data:
            self.indices_label.setText(f"<span style='color:red'>Error fetching indices: {data['error']}</span>")
            return
        html = (
            f"<b>Updated:</b> {data.get('updated','')}<br>"
            f"<b>SFI:</b> {data.get('solarflux','')} &nbsp; "
            f"<b>A:</b> {data.get('aindex','')} &nbsp; "
            f"<b>K:</b> {data.get('kindex','')}<br>"
            f"<b>X-ray:</b> {data.get('xray','')} &nbsp; "
            f"<b>Sunspots:</b> {data.get('sunspots','')}<br>"
            f"<b>Solar Wind:</b> {data.get('solarwind','')} km/s &nbsp; "
            f"<b>Mag Field:</b> {data.get('magneticfield','')} nT<br>"
            f"<b>Signal/Noise:</b> {data.get('signalnoise','')}"
        )
        self.indices_label.setText(html)

class ZoomableWebView(QWebEngineView):
    def __init__(self, url):
        super().__init__()
        self.setUrl(QUrl(url))
        self.zoom = 1.0
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.overlay = ZoomOverlay(self)
        self.overlay.resize(self.size())
        self.overlay.show()
        self.resized = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "overlay"):
            self.overlay.resize(self.size())

class ZoomOverlay(QWidget):
    def __init__(self, webview):
        super().__init__(webview)
        self.webview = webview
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.raise_()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.webview.zoom = min(self.webview.zoom + 0.1, 3.0)
            self.webview.setZoomFactor(self.webview.zoom)
        elif event.button() == Qt.RightButton:
            self.webview.zoom = max(self.webview.zoom - 0.1, 0.3)
            self.webview.setZoomFactor(self.webview.zoom)
        event.accept()

class PropagationInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Propagation Info (Real-Time)")
        self.resize(800, 900)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Get up to 3 widgets from preferences, or default
        widgets = []
        if parent and hasattr(parent, "prefs"):
            widgets = parent.prefs.get("solar_widgets", [])
        if not widgets:
            widgets = ["https://www.hamqsl.com/solar101vhfper.php"]

        self.webviews = []
        for url in widgets[:3]:
            webview = ZoomableWebView(url)
            webview.setMinimumHeight(260)  # Tiny bit smaller
            layout.addWidget(webview, stretch=2)
            self.webviews.append(webview)

        # Button row (side by side, slightly bigger)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedSize(140, 42)
        self.refresh_btn.clicked.connect(self.flash_refresh)
        btn_row.addWidget(self.refresh_btn)

        self.back_btn = QPushButton("Back")
        self.back_btn.setFixedSize(140, 42)
        self.back_btn.clicked.connect(self.flash_back)
        btn_row.addWidget(self.back_btn)

        layout.addLayout(btn_row)
        self.setLayout(layout)

        dark_mode = False
        if parent and hasattr(parent, "prefs"):
            dark_mode = parent.prefs.get("dark_mode", False)
        self.apply_style(dark_mode)

    def apply_style(self, dark_mode):
        if dark_mode:
            self.base_btn_style = """
                QPushButton {
                    color: white;
                    background-color: #222;
                    font-size: 14pt;
                    border: 1px solid #555;
                    border-radius: 16px;
                    padding: 6px 24px;
                    margin: 6px 0;
                }
                QPushButton:hover {
                    background: #3a3f4b;
                }
                QPushButton:pressed {
                    background: #2196F3;
                }
            """
        else:
            self.base_btn_style = """
                QPushButton {
                    color: #222;
                    background-color: #f5f5f5;
                    font-size: 14pt;
                    border: 1px solid #bbb;
                    border-radius: 16px;
                    padding: 6px 24px;
                    margin: 6px 0;
                }
                QPushButton:hover {
                    background: #e0e0e0;
                }
                QPushButton:pressed {
                    background: #2196F3;
                    color: #fff;
                }
            """
        self.setStyleSheet(self.base_btn_style)

    def flash_refresh(self):
        self._flash_button(self.refresh_btn)
        for webview in self.webviews:
            webview.reload()

    def flash_back(self):
        self._flash_button(self.back_btn)
        QTimer.singleShot(200, self.close)

    def _flash_button(self, button):
        orig_style = button.styleSheet()
        button.setStyleSheet("background-color: #2196F3; color: white;")
        QTimer.singleShot(200, lambda: button.setStyleSheet(""))