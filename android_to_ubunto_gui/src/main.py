# This file serves as the entry point for the GUI application. It initializes the GUI and handles the main application loop.

import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()