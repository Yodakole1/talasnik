import os
import json

PREFS_FILE = "talasnik_prefs.json"
DEFAULT_PREFS = {
    "dark_mode": False,
    "rows": 20,
    "font_family": "Arial",
    "font_size": 15,
    "morse_wpm": 30,
    "solar_widgets": [
        "https://www.hamqsl.com/solar101vhfper.php"
    ],
    "morse_mode": "Spacebar (short/long)",
    "show_morse_alphabet": False,
    "hamqth_username": "",
    "hamqth_password": ""
}

def load_prefs():
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, "r") as f:
            return {**DEFAULT_PREFS, **json.load(f)}
    return DEFAULT_PREFS.copy()

def save_prefs(prefs):
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f)