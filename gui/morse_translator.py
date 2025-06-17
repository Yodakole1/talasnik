from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFileDialog, QComboBox, QSizePolicy, QWidget, QGridLayout
)
from PyQt5.QtCore import Qt

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', '/': '-..-.', '@': '.--.-.',
    '-': '-....-', '(': '-.--.', ')': '-.--.-', ' ': '/'
}
REVERSE_MORSE_CODE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}

def text_to_morse(text):
    result = []
    for char in text.upper():
        if char in MORSE_CODE_DICT:
            result.append(MORSE_CODE_DICT[char])
        else:
            result.append('?')
    return ' '.join(result)

def morse_to_text(morse):
    result = []
    for code in morse.strip().split(' '):
        if code == '':
            continue
        result.append(REVERSE_MORSE_CODE_DICT.get(code, '?'))
    return ''.join(result).replace('/', ' ')

class MorseTranslatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Morse Code Translator")
        self.resize(600, 360)
        self.setMinimumSize(420, 240)
        layout = QVBoxLayout(self)

        # Mode selection
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Text → Morse", "Morse → Text"])
        self.mode_combo.currentIndexChanged.connect(self.translate)
        layout.addWidget(self.mode_combo)

        # Input/output
        io_layout = QHBoxLayout()
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("Type or paste your text or Morse code here...")
        self.input_edit.setFixedHeight(70)
        self.input_edit.textChanged.connect(self.translate)
        io_layout.addWidget(self.input_edit, 1)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setFixedHeight(70)
        io_layout.addWidget(self.output_edit, 1)
        layout.addLayout(io_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load File")
        self.load_btn.clicked.connect(self.load_file)
        btn_layout.addWidget(self.load_btn)

        self.save_btn = QPushButton("Save Output")
        self.save_btn.clicked.connect(self.save_file)
        btn_layout.addWidget(self.save_btn)

        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        # Morse alphabet reference as a grid
        grid_widget = QWidget()
        grid = QGridLayout()
        grid.setSpacing(4)
        letters = [
            ('A', '.-'),   ('B', '-...'), ('C', '-.-.'), ('D', '-..'),  ('E', '.'),
            ('F', '..-.'), ('G', '--.'),  ('H', '....'), ('I', '..'),   ('J', '.---'),
            ('K', '-.-'),  ('L', '.-..'), ('M', '--'),   ('N', '-.'),   ('O', '---'),
            ('P', '.--.'), ('Q', '--.-'), ('R', '.-.'),  ('S', '...'),  ('T', '-'),
            ('U', '..-'),  ('V', '...-'), ('W', '.--'),  ('X', '-..-'), ('Y', '-.--'),
            ('Z', '--..'),
            ('0', '-----'), ('1', '.----'), ('2', '..---'), ('3', '...--'), ('4', '....-'),
            ('5', '.....'), ('6', '-....'), ('7', '--...'), ('8', '---..'), ('9', '----.')
        ]
        cols = 7
        for idx, (char, code) in enumerate(letters):
            row = idx // cols
            col = idx % cols
            label = QLabel(f"<b>{char}</b>: {code}")
            label.setStyleSheet("font-size: 11pt; color: #888;")
            grid.addWidget(label, row, col)
        grid_widget.setLayout(grid)
        layout.addWidget(grid_widget)

        self.setLayout(layout)
        self.translate()

    def translate(self):
        mode = self.mode_combo.currentText()
        inp = self.input_edit.toPlainText()
        if mode == "Text → Morse":
            self.output_edit.setPlainText(text_to_morse(inp))
        else:
            self.output_edit.setPlainText(morse_to_text(inp))

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.input_edit.setPlainText(f.read())

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Output", "morse.txt", "Text Files (*.txt);;All Files (*)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.output_edit.toPlainText())