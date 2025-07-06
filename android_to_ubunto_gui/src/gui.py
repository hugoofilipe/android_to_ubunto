# gui.py

import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QApplication
import subprocess
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android to Ubuntu Controller")
        self.resize(500, 180)  # Increased window size (width, height)

        self.status_label = QLabel("Status: Disconnected")
        self.unlock_button = QPushButton("Start Unlock phone")
        self.weakup_button = QPushButton("Wakeup Phone")
        self.ipad_button = QPushButton("Turn On Ipad")
        self.close_button = QPushButton("Close")
        self.ipad_on = False
        self.uxplay_process = None
        self.unlock_process = None

        self.unlock_button.clicked.connect(self.toggle_unlock_script)
        self.ipad_button.clicked.connect(self.toggle_ipad)
        self.weakup_button.clicked.connect(self.wakeup_phone)
        self.close_button.clicked.connect(self.close_program)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.unlock_button)
        layout.addWidget(self.weakup_button)
        layout.addWidget(self.ipad_button)
        layout.addWidget(self.close_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.weakup_button.setEnabled(False)  # Disable at start

    def toggle_unlock_script(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../android_to_ubunto.sh'))
        if self.unlock_process is None:
            # Start android_to_ubunto.sh with 'start'
            self.unlock_process = subprocess.Popen(['bash', script_path, 'start'])
            self.status_label.setText("Status: Unlock Script Running")
            self.unlock_button.setText("Stop adb phone")
            self.weakup_button.setEnabled(True)
        else:
            # Stop android_to_ubunto.sh with 'stop'
            subprocess.Popen(['bash', script_path, 'stop'])
            self.status_label.setText("Status: Disconnected")
            self.unlock_button.setText("Start Unlock Script")
            self.unlock_process = None
            self.weakup_button.setEnabled(False)
            if self.ipad_on:
                self.toggle_ipad(force_off=True)

    def toggle_ipad(self, force_off=False):
        if not self.ipad_on and not force_off:
            try:
                self.uxplay_process = subprocess.Popen(['uxplay', '-avdec', '-vs', 'ximagesink'])
                self.ipad_button.setText("Turn Off Ipad")
                self.status_label.setText("Status: iPad Mirroring On")
                self.ipad_on = True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start uxplay: {e}")
        else:
            if self.uxplay_process is not None:
                try:
                    self.uxplay_process.terminate()
                    self.uxplay_process.wait(timeout=5)
                except Exception:
                    self.uxplay_process.kill()
                self.uxplay_process = None
            self.ipad_button.setText("Turn On Ipad")
            if not self.unlock_process:
                self.status_label.setText("Status: Disconnected")
            else:
                self.status_label.setText("Status: Unlock Script Running")
            self.ipad_on = False

    def wakeup_phone(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../android_to_ubunto.sh'))
        try:
            subprocess.run(['bash', script_path, 'wakeup'])
            self.status_label.setText("Status: Phone Woken Up")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to wake up phone: {e}")

    def close_program(self):
        # Ensure all processes are terminated when closing the app via button
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../android_to_ubunto.sh'))
        if self.unlock_process is not None:
            subprocess.Popen(['bash', script_path, 'stop'])
            self.unlock_process = None
        if self.uxplay_process is not None:
            self.uxplay_process.terminate()
            try:
                self.uxplay_process.wait(timeout=5)
            except Exception:
                self.uxplay_process.kill()
        # Kill all adb processes just in case
        subprocess.Popen(['pkill', '-f', 'adb'])
        QApplication.quit()

    def closeEvent(self, event):
        # Ensure all processes are terminated when closing the app via window close
        self.close_program()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())