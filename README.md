# Talasnik

Talasnik is a modern ham radio logbook and utility suite for Linux and Windows, built with Python and PyQt5.

## Features

- Ham logbook
- Antenna calculator
- Morse code practicer and translator
- Propagation tools
- Radio programming utilities

## Installation

1. Clone this repository:
    ```
    git clone https://github.com/yourusername/talasnik.git
    cd talasnik
    ```

2. Install dependencies (Python 3.8+ recommended):
    ```
    pip install -r requirements.txt
    ```

3. Run the app:
    ```
    python gui.py
    ```

## App Icon

- Place your icon file (e.g. `icon.png` or `icon.ico`) in the `gui/` folder.
- To use the icon in the app, add this to the top of `main_window.py`:
    ```python
    from PyQt5.QtGui import QIcon
    ```
  And in your `MainWindow.__init__` or `main()`:
    ```python
    self.setWindowIcon(QIcon("gui/icon.png"))  # or .ico for Windows
    ```
- For PyInstaller, see below.

## Building a Windows `.exe`

1. Install [PyInstaller](https://pyinstaller.org/):
    ```
    pip install pyinstaller
    ```

2. Build the executable:
    ```
    pyinstaller --noconfirm --onefile --windowed --icon=gui/icon.ico gui.py
    ```
    - Use `.ico` for Windows icons.
    - The `.exe` will be in the `dist/` folder.

3. Distribute the `dist/talasnik.exe` file.

## License

MIT License

---

**Credits:**  
Developed by [Your Name]  