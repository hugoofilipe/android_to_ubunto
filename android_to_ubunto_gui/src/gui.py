# gui.py

import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QApplication
import subprocess
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android to Ubuntu Controller")

        self.status_label = QLabel("Status: Disconnected")
        self.start_button = QPushButton("Start Unlock Script")
        self.stop_button = QPushButton("Stop Unlock Script")

        self.start_button.clicked.connect(self.start_connection)
        self.stop_button.clicked.connect(self.stop_connection)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.process = None

    def start_connection(self):
        if self.process is None:
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../adb_unlock.sh'))
            self.process = subprocess.Popen(['bash', script_path])
            self.status_label.setText("Status: Unlock Script Running")
        else:
            QMessageBox.information(self, "Info", "Unlock script is already running.")

    def stop_connection(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None
            self.status_label.setText("Status: Disconnected")
        else:
            QMessageBox.information(self, "Info", "No unlock script running.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())