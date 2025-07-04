from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QInputDialog, QLineEdit, QMessageBox, QDialogButtonBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QSettings
import os
import xml.etree.ElementTree as ET
import tempfile
import folium
import requests
from gui.prefs import load_prefs, save_prefs


def get_hamqth_credentials(parent=None):
    prefs = load_prefs()
    username = prefs.get("hamqth_username", "")
    password = prefs.get("hamqth_password", "")
    if not username or not password:
        msg = (
            "Enter your HamQTH.com username and password.<br>"
            "If you don't have an account, <a href='https://www.hamqth.com/signup.php'>sign up here</a>."
        )
        dlg = QDialog(parent)
        dlg.setWindowTitle("HamQTH Login")
        layout = QVBoxLayout(dlg)
        label = QLabel(msg)
        label.setOpenExternalLinks(True)
        layout.addWidget(label)
        user_input = QLineEdit()
        user_input.setPlaceholderText("Username")
        pass_input = QLineEdit()
        pass_input.setPlaceholderText("Password")
        pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(user_input)
        layout.addWidget(pass_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        if dlg.exec_() == QDialog.Accepted:
            username = user_input.text().strip()
            password = pass_input.text().strip()
            if username and password:
                prefs["hamqth_username"] = username
                prefs["hamqth_password"] = password
                save_prefs(prefs)
            else:
                return None, None
        else:
            return None, None
    return username, password

def hamqth_session(username, password):
    """Get HamQTH session key, return None if login fails."""
    url = f"https://www.hamqth.com/xml.php?u={username}&p={password}"
    r = requests.get(url, timeout=10)
    ns = {'h': 'https://www.hamqth.com'}
    root = ET.fromstring(r.text)
    error = root.find("h:session/h:error", ns)
    if error is not None:
        return None
    session = root.find("h:session", ns)
    key = session.find("h:session_id", ns).text if session is not None else None
    return key

def lookup_latlon(callsign, username, password):
    try:
        session_id = hamqth_session(username, password)
        if not session_id:
            return None
        url = f"https://www.hamqth.com/xml.php?id={session_id}&callsign={callsign}&prg=Talasnik"
        r = requests.get(url, timeout=10)
        ns = {'h': 'https://www.hamqth.com'}
        root = ET.fromstring(r.text)
        search = root.find("h:search", ns)
        if search is None:
            return None
        lat = search.findtext("h:latitude", default="", namespaces=ns)
        lon = search.findtext("h:longitude", default="", namespaces=ns)
        city = search.findtext("h:qth", default="", namespaces=ns)
        country = search.findtext("h:country", default="", namespaces=ns)
        if lat and lon:
            return float(lat), float(lon), city, country
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
        # Set label and window text color based on dark mode
        if dark_mode:
            label.setStyleSheet("color: white; font-size: 16pt;")
            self.setStyleSheet("color: white; background: #23272e;")
        else:
            label.setStyleSheet("color: #23272e; font-size: 16pt;")
            self.setStyleSheet("color: #23272e; background: #f5f5f5;")
        layout.addWidget(label)

        # --- Prompt for credentials if needed ---
        username, password = get_hamqth_credentials(self)
        if not username or not password:
            QMessageBox.warning(self, "No Credentials", "HamQTH credentials are required to use the QSO map.")
            self.reject()
            return

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
        tmp_file.close()
        fmap.save(tmp_file.name)

        self.webview = QWebEngineView()
        local_url = QUrl.fromLocalFile(os.path.abspath(tmp_file.name))
        self.webview.setUrl(local_url)
        layout.addWidget(self.webview)

        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        self.setLayout(layout)
