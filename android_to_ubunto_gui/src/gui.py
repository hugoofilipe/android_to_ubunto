# gui.py

import sys
import os
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QApplication
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android to Ubuntu Controller")
        self.resize(500, 200)  # Increased window size (width, height)

        self.status_label = QLabel("Status: Disconnected")
        self.unlock_button = QPushButton("Start Unlock phone")
        self.weakup_button = QPushButton("Wakeup Phone")
        self.ipad_button = QPushButton("Turn On Ipad")
        self.obs_button = QPushButton("OBS Stream")
        self.close_button = QPushButton("Close")
        
        self.ipad_on = False
        self.uxplay_process = None
        self.unlock_process = None
        self.obs_process = None

        self.unlock_button.clicked.connect(self.toggle_unlock_script)
        self.ipad_button.clicked.connect(self.toggle_ipad)
        self.weakup_button.clicked.connect(self.wakeup_phone)
        self.obs_button.clicked.connect(self.start_obs_stream)
        self.close_button.clicked.connect(self.close_program)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.unlock_button)
        layout.addWidget(self.weakup_button)
        layout.addWidget(self.ipad_button)
        layout.addWidget(self.obs_button)
        layout.addWidget(self.close_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.weakup_button.setEnabled(False)

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

    def start_obs_stream(self):
        try:
            # Load environment variables from .env file
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
            env_vars = {}
            
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Remove quotes if present
                            value = value.strip('"\'')
                            env_vars[key] = value
            
            obs_ini_path = env_vars.get('OBSGLOBALINIPATH', '~/.config/obs-studio/global.ini')
            obs_ini_path = os.path.expanduser(obs_ini_path)
            
            # Remove the OBS config file
            if os.path.exists(obs_ini_path):
                os.remove(obs_ini_path)
                print(f"Removed {obs_ini_path}")
            
            # Start OBS
            self.obs_process = subprocess.Popen(['obs'])
            self.status_label.setText("Status: OBS Stream Started")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start OBS stream: {e}")

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
        if self.obs_process is not None:
            self.obs_process.terminate()
            try:
                self.obs_process.wait(timeout=5)
            except Exception:
                self.obs_process.kill()
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