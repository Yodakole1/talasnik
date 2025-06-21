import sys
from gui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QIcon

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    window = MainWindow()
    window.setWindowIcon(QIcon("gui/app_logo.png"))
    window.showFullScreen()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()