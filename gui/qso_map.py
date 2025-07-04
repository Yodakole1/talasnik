import tempfile
import folium
import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QInputDialog, QLineEdit, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os
import xml.etree.ElementTree as ET

# --- Hardcoded HamQTH credentials ---
HAMQTH_USERNAME = "YU3CBA"
HAMQTH_PASSWORD = "WZVI18izRo3tpN"

def hamqth_session(username, password):
    """Get HamQTH session key, return None if login fails."""
    url = f"https://www.hamqth.com/xml.php?u={username}&p={password}"
    r = requests.get(url, timeout=10)
    print("HamQTH login response:", r.text)  # Debug
    ns = {'h': 'https://www.hamqth.com'}
    root = ET.fromstring(r.text)
    error = root.find("h:session/h:error", ns)
    if error is not None:
        print("HamQTH error:", error.text)
        return None
    session = root.find("h:session", ns)
    key = session.find("h:session_id", ns).text if session is not None else None
    return key

def lookup_latlon(callsign, username, password):
    """Lookup latitude, longitude, city, and country using HamQTH API."""
    try:
        session_id = hamqth_session(username, password)
        if not session_id:
            print(f"Failed to get HamQTH session for user {username}")
            return None
        url = f"https://www.hamqth.com/xml.php?id={session_id}&callsign={callsign}&prg=Talasnik"
        r = requests.get(url, timeout=10)
        print(f"HamQTH search response for {callsign}:", r.text)  # Debug

        # Handle XML namespace
        ns = {'h': 'https://www.hamqth.com'}
        root = ET.fromstring(r.text)
        search = root.find("h:search", ns)
        if search is None:
            print(f"No search result for {callsign}: {r.text}")
            return None
        lat = search.findtext("h:latitude", default="", namespaces=ns)
        lon = search.findtext("h:longitude", default="", namespaces=ns)
        city = search.findtext("h:qth", default="", namespaces=ns)
        country = search.findtext("h:country", default="", namespaces=ns)
        if lat and lon:
            return float(lat), float(lon), city, country
        else:
            print(f"No latitude/longitude for {callsign}: {r.text}")
    except Exception as e:
        print(f"Error looking up {callsign}: {e}")
    return None

class QSOMapDialog(QDialog):
    def __init__(self, logbook, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QSO Map")
        self.resize(900, 600)
        layout = QVBoxLayout(self)

        # --- Use hardcoded credentials ---
        username = HAMQTH_USERNAME
        password = HAMQTH_PASSWORD

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
        marker_count = 0
        for call in set(callsigns):
            loc = lookup_latlon(call, username, password)
            if loc:
                lat, lon, city, country = loc
                popup = f"{call}<br>{city}, {country}"
                folium.Marker(location=[lat, lon], popup=popup).add_to(fmap)
                marker_count += 1

        if marker_count == 0:
            QMessageBox.warning(self, "No Results", "No valid locations found for your callsigns.")

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
