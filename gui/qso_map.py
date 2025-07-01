import tempfile
import folium
import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os

def lookup_latlon(callsign):
    """Very basic lookup using HamQTH API (no login, country centroid fallback)."""
    try:
        url = f"https://api.hamdb.org/{callsign}/json/hamdb"
        r = requests.get(url, timeout=5)
        data = r.json()
        if "hamdb" in data and "lat" in data["hamdb"] and "long" in data["hamdb"]:
            return float(data["hamdb"]["lat"]), float(data["hamdb"]["long"])
    except Exception:
        pass
    return None

class QSOMapDialog(QDialog):
    def __init__(self, logbook, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QSO Map")
        self.resize(900, 600)
        layout = QVBoxLayout(self)

        label = QLabel("World map of QSOs (callsign locations are approximate)")
        dark_mode = False
        if parent and hasattr(parent, "prefs"):
            dark_mode = parent.prefs.get("dark_mode", False)
        if dark_mode:
            label.setStyleSheet("color: white; font-size: 16pt;")
        else:
            label.setStyleSheet("color: #23272e; font-size: 16pt;")
        layout.addWidget(label)

        # Gather callsigns from logbook
        callsigns = []
        col = None
        for i in range(logbook.columnCount()):
            header = logbook.horizontalHeaderItem(i)
            if header and header.text().lower().startswith("call"):
                col = i
                break

        if col is not None:
            for row in range(logbook.rowCount()):
                item = logbook.item(row, col)
                if item:
                    callsigns.append(item.text().strip().upper())

        # Build map
        fmap = folium.Map(location=[20, 0], zoom_start=2)
        for call in set(callsigns):
            loc = lookup_latlon(call)
            if loc:
                folium.Marker(location=loc, popup=call).add_to(fmap)

        # Save map to temp file safely
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        tmp_file.close()  # Close file handle so folium can write to it
        fmap.save(tmp_file.name)

        self.webview = QWebEngineView()
        local_url = QUrl.fromLocalFile(os.path.abspath(tmp_file.name))
        self.webview.setUrl(local_url)
        layout.addWidget(self.webview)

        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        self.setLayout(layout)
