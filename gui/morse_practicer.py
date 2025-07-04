from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHBoxLayout, QSpinBox
from PyQt5.QtCore import Qt, QTimer
import time

MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
    '...--': '3', '....-': '4', '.....': '5', '-....': '6',
    '--...': '7', '---..': '8', '----.': '9'
}

class MorsePracticerDialog(QDialog):
    def __init__(self, mode, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Morse Code Practicer")
        self.resize(500, 340)
        self.mode = mode
        self.morse = ""
        self.text = ""
        self.last_press = 0
        self.input_active = False

        # --- WPM selector ---
        self.prefs = getattr(parent, "prefs", {}) if parent else {}
        self.wpm = self.prefs.get("morse_wpm", 30)
        wpm_row = QHBoxLayout()
        wpm_row.addStretch(1)
        wpm_label = QLabel("WPM:")
        self.wpm_spin = QSpinBox()
        self.wpm_spin.setRange(5, 60)
        self.wpm_spin.setValue(self.wpm)
        self.wpm_spin.setFixedWidth(60)
        self.wpm_spin.valueChanged.connect(self.set_wpm)
        wpm_row.addWidget(wpm_label)
        wpm_row.addWidget(self.wpm_spin)

        # Detect dark mode from parent if available
        dark_mode = False
        if parent and hasattr(parent, "prefs"):
            dark_mode = parent.prefs.get("dark_mode", False)

        wpm_color = "white" if dark_mode else "#23272e"
        wpm_label.setStyleSheet(f"color: {wpm_color}; font-size: 12pt; font-family: 'Segoe UI', 'Arial', sans-serif;")
        self.wpm_spin.setStyleSheet(f"color: {wpm_color}; font-size: 12pt; font-family: 'Segoe UI', 'Arial', sans-serif;")

        if dark_mode:
            self.dot_dash_label = QLabel("Press Start and begin typing Morse code.")
            self.dot_dash_label.setStyleSheet(
                "font-size: 18pt; font-family: 'Segoe UI', 'Arial', sans-serif; color: white;"
            )
            self.text_label = QLabel("")
            self.text_label.setStyleSheet(
                "font-size: 18pt; font-family: 'Segoe UI', 'Arial', sans-serif; color: #4fc3f7; font-weight: bold;"
            )
        else:
            self.dot_dash_label = QLabel("Press Start and begin typing Morse code.")
            self.dot_dash_label.setStyleSheet(
                "font-size: 18pt; font-family: 'Segoe UI', 'Arial', sans-serif; color: #23272e;"
            )
            self.text_label = QLabel("")
            self.text_label.setStyleSheet(
                "font-size: 18pt; font-family: 'Segoe UI', 'Arial', sans-serif; color: #1976d2; font-weight: bold;"
            )

        # Morse alphabet string
        self.morse_alphabet_label = None
        show_alphabet = False
        if parent and hasattr(parent, "prefs"):
            show_alphabet = parent.prefs.get("show_morse_alphabet", False)

        if show_alphabet:
            # Build a readable Morse alphabet table
            morse_lines = []
            for k in sorted(MORSE_CODE_DICT, key=lambda x: (len(x), x)):
                if k.isalpha() or k.isdigit():
                    continue
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
                code = [k for k, v in MORSE_CODE_DICT.items() if v == letter]
                if code:
                    morse_lines.append(f"{letter}: {code[0]}")
            morse_table = "   ".join(morse_lines[:13]) + "\n" + "   ".join(morse_lines[13:])
            self.morse_alphabet_label = QLabel(morse_table)
            self.morse_alphabet_label.setStyleSheet(
                "font-size: 12pt; font-family: 'Segoe UI', 'Arial', sans-serif; color: #888;"
            )

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.toggle_practice)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_to_file)
        self.save_btn.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.addLayout(wpm_row)
        if self.morse_alphabet_label:
            layout.addWidget(self.morse_alphabet_label)
        layout.addWidget(self.dot_dash_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)

        # Set initial timeout based on WPM
        self.key_timer = QTimer(self)
        self.key_timer.setSingleShot(True)
        self.key_timer.timeout.connect(self.end_letter)
        self.update_letter_timeout()

    def set_wpm(self, value):
        self.wpm = value
        self.update_letter_timeout()
        # Save to preferences if possible
        if self.prefs is not None:
            self.prefs["morse_wpm"] = value
            # Save prefs to disk if parent has save_prefs
            parent = self.parent()
            if parent and hasattr(parent, "prefs"):
                parent.prefs["morse_wpm"] = value
                try:
                    from gui.main_window import save_prefs
                    save_prefs(parent.prefs)
                except Exception:
                    pass

    def update_letter_timeout(self):
        # Standard: 1 WPM = 1200 ms per dit, so letter timeout = 60000/(50*WPM) ms per dot
        # For end-of-letter, a common value is 3x dot length
        dot_length_ms = 1200 / self.wpm
        self.letter_timeout = int(dot_length_ms * 3)
        # No need to set timer interval here, just use self.letter_timeout when starting timer

    def toggle_practice(self):
        if not self.input_active:
            self.start()
        else:
            self.stop()

    def start(self):
        self.morse = ""
        self.text = ""
        self.dot_dash_label.setText("Type Morse code:")
        self.text_label.setText("")
        self.input_active = True
        self.setFocus()
        if self.mode.startswith("Spacebar"):
            self.grabKeyboard()
        self.start_btn.setText("Stop")
        self.save_btn.setEnabled(False)

    def stop(self):
        self.input_active = False
        try:
            self.releaseKeyboard()
        except Exception:
            pass
        self.dot_dash_label.setText("Press Start and begin typing Morse code.")
        self.start_btn.setText("Start")
        self.save_btn.setEnabled(True)

    def closeEvent(self, event):
        try:
            self.releaseKeyboard()
        except Exception:
            pass
        event.accept()

    def keyPressEvent(self, event):
        if not self.input_active:
            return
        if self.mode.startswith("Spacebar"):
            if event.key() == Qt.Key_Space:
                self.last_press = time.time()
                self.key_timer.stop()
            elif event.key() == Qt.Key_Escape:
                self.stop()
        elif event.key() == Qt.Key_Escape:
            self.stop()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if not self.input_active:
            return
        if self.mode.startswith("Spacebar"):
            if event.key() == Qt.Key_Space:
                duration = time.time() - self.last_press
                if duration < 0.18:
                    self.morse += "."
                else:
                    self.morse += "-"
                self.update_display()
                self.key_timer.stop()
                self.key_timer.start(self.letter_timeout)
        else:
            super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if not self.input_active:
            return
        if self.mode.startswith("Mouse"):
            if event.button() == Qt.LeftButton:
                self.morse += "."
                self.update_display()
                self.key_timer.stop()
                self.key_timer.start(self.letter_timeout)
            elif event.button() == Qt.RightButton:
                self.morse += "-"
                self.update_display()
                self.key_timer.stop()
                self.key_timer.start(self.letter_timeout)
        else:
            super().mousePressEvent(event)

    def end_letter(self):
        if self.morse:
            letter = MORSE_CODE_DICT.get(self.morse, None)
            if letter is None:
                self.text += "invalid morse code"
            else:
                self.text += letter
            self.text_label.setText(self.text)
            self.morse = ""
            self.dot_dash_label.setText("")
        else:
            self.dot_dash_label.setText("")
        self.update_display()

    def update_display(self):
        self.dot_dash_label.setText(self.morse)
        # Live translation
        if self.morse:
            letter = MORSE_CODE_DICT.get(self.morse, "invalid morse code")
            self.text_label.setText(self.text + letter)
        else:
            self.text_label.setText(self.text)

    def save_to_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Morse Practice",
            "morse.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.text)
            except Exception as e:
                self.dot_dash_label.setText(f"Error saving: {e}")