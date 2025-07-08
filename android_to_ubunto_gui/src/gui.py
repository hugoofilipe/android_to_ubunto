# gui.py

import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QApplication, QTextEdit
import subprocess
import os
import re

from dotenv import dotenv_values
env_vars = dotenv_values(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env')))

if 'PWD' not in env_vars and 'OBSGLOBALINIPATH' not in env_vars:
    raise ValueError("Required environment variables 'PWD' or 'OBSGLOBALINIPATH' not found in .env file.")
    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android to Ubuntu Controller")
        self.resize(500, 400)

        self.status_label = QLabel("Status: Disconnected")
        self.battery_label = QLabel("Battery: --%")
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setMaximumHeight(120)

        self.unlock_button = QPushButton("Start Unlock phone")
        self.weakup_button = QPushButton("Wakeup/Sleep")
        self.ipad_button = QPushButton("Turn On Ipad")
        self.obs_button = QPushButton("OBS Stream")
        self.printing_button = QPushButton("Printing (basic)")
        self.close_button = QPushButton("Close")
        self.deep_print_button = QPushButton("Printing (deep)")
        self.use_pin_button = QPushButton("Use PIN")  # New button

        # Track unlock state
        self.device_unlocked = False

        # Disable buttons that require unlock at start
        self.use_pin_button.setEnabled(False)
        self.printing_button.setEnabled(False)
        self.deep_print_button.setEnabled(False)

        # ...existing state...
        self.ipad_on = False
        self.uxplay_process = None
        self.unlock_process = None
        self.obs_process = None

        self.unlock_button.clicked.connect(self.toggle_unlock_script)
        self.ipad_button.clicked.connect(self.toggle_ipad)
        self.weakup_button.clicked.connect(self.wakeup_phone)
        self.obs_button.clicked.connect(self.start_obs_stream)
        self.printing_button.clicked.connect(self.print_screen_text)
        self.close_button.clicked.connect(self.close_program)
        self.deep_print_button.clicked.connect(lambda: self.deep_print_screen_text(scroll_times=2))
        self.use_pin_button.clicked.connect(self.use_pin_click)  # Connect new button

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.battery_label)
        layout.addWidget(self.text_box)
        layout.addWidget(self.unlock_button)
        layout.addWidget(self.weakup_button)
        layout.addWidget(self.obs_button)
        layout.addWidget(self.ipad_button)
        layout.addWidget(self.printing_button)
        layout.addWidget(self.deep_print_button)
        layout.addWidget(self.use_pin_button)  # Add new button to layout
        layout.addWidget(self.close_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.weakup_button.setEnabled(False)
        self.update_battery_label()

    def update_battery_label(self):
        try:
            output = subprocess.check_output(
                ["adb", "shell", "dumpsys", "battery"], encoding="utf-8"
            )
            match = re.search(r"level: (\d+)", output)
            if match:
                percent = int(match.group(1))
                if percent < 15:
                    self.battery_label.setText(f'Battery: <span style="color:red">{percent}%</span>')
                else:
                    self.battery_label.setText(f"Battery: {percent}%")
            else:
                self.battery_label.setText("Battery: N/A")
        except Exception:
            self.battery_label.setText("Battery: N/A")

    def toggle_unlock_script(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../android_to_ubunto.sh'))
        if self.unlock_process is None:
            # Start android_to_ubunto.sh with 'start'
            self.unlock_process = subprocess.Popen(['bash', script_path, 'start'])
            self.status_label.setText("Status: Unlock Script Running")
            self.unlock_button.setText("Stop adb phone")
            self.weakup_button.setEnabled(True)
            # Enable buttons that require unlock
            self.device_unlocked = True
            self.use_pin_button.setEnabled(True)
            self.printing_button.setEnabled(True)
            self.deep_print_button.setEnabled(True)
        else:
            # Stop android_to_ubunto.sh with 'stop'
            subprocess.Popen(['bash', script_path, 'stop'])
            self.status_label.setText("Status: Disconnected")
            self.unlock_button.setText("Start Unlock Script")
            self.unlock_process = None
            self.weakup_button.setEnabled(False)
            # Disable buttons that require unlock
            self.device_unlocked = False
            self.use_pin_button.setEnabled(False)
            self.printing_button.setEnabled(False)
            self.deep_print_button.setEnabled(False)
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

    def print_screen_text(self):
        """
        Shows all visible text from the Android screen in the UI text box (max 6 lines with scroll).
        """
        try:
            # Dump UI hierarchy to a file on the device
            subprocess.check_output("adb shell uiautomator dump /sdcard/window_dump.xml", shell=True)
            # Pull the file to the local machine
            subprocess.check_output("adb pull /sdcard/window_dump.xml", shell=True)
            # Read the XML file
            with open("window_dump.xml", "r", encoding="utf-8") as f:
                xml_content = f.read()
            texts = re.findall(r'text="([^"]*)"', xml_content)
            os.remove(f"window_dump.xml")  # Clean up the pulled file
            filtered = [t for t in texts if t.strip()]
            if filtered:
                self.text_box.setPlainText('\n'.join(filtered))
                self.status_label.setText("Status: Screen text shown below")
            else:
                self.text_box.setPlainText("(No text found on screen)")
                self.status_label.setText("Status: No text found on screen")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show screen text: {e}")

    def deep_print_screen_text(self, scroll_times=5):
        """
        Scrolls and dumps the Android screen multiple times, showing all unique visible text in the UI text box.
        Appends new data at the end for each scroll.
        """
        subprocess.run(["adb", "shell", "input", "swipe", "500", "500", "500", "1500", "300"], check=True)
        self.text_box.setPlainText("Starting deep printing screen text...")
        QApplication.processEvents()
        self.status_label.setText("Status: Deep Printing Screen Text...")

        try:
            all_texts = set()
            output_lines = []
            xml_files = []
            for i in range(scroll_times):
                xml_file = f"window_dump_{i}.xml"
                xml_files.append(xml_file)
                # Dump and pull in one go, avoid shell=True for safety
                subprocess.run(["adb", "shell", "uiautomator", "dump", f"/sdcard/{xml_file}"], check=True)
                subprocess.run(["adb", "pull", f"/sdcard/{xml_file}", xml_file], check=True)
                with open(xml_file, "r", encoding="utf-8") as f:
                    found = []
                    for t in re.findall(r'text="([^"]*)"', f.read()):
                        if t.strip() and t not in all_texts:
                            found.append(t)
                            all_texts.add(t)
                if found:
                    output_lines.append(f"--- Scroll {i+1} ---")
                    output_lines.extend(found)
                # Scroll (swipe up), but skip after last iteration
                if i < scroll_times - 1:
                    subprocess.run(["adb", "shell", "input", "swipe", "500", "1500", "500", "500", "300"], check=True)
            if output_lines:
                self.text_box.setPlainText('\n'.join(output_lines))
                self.status_label.setText("Status: Deep screen text shown below")
            else:
                self.text_box.setPlainText("(No text found on screen)")
                self.status_label.setText("Status: No text found on screen")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to deep print screen text: {e}")
        finally:
            # Remove all pulled xml files locally
            for xml_file in xml_files:
                try:
                    os.remove(xml_file)
                    subprocess.run(["adb", "shell", "rm", f"/sdcard/{xml_file}"], check=True)
                    print(f"Removed {xml_file}")
                except FileNotFoundError:
                    pass
            # Remove all dump files from the device
            self.status_label.setText("Status: Deep Printing Completed")

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

    # def closeEvent(self, event):
    #     # Ensure all processes are terminated when closing the app via window close
    #     self.close_program()
    #     event.accept()

    def use_pin_click(self):
        """
        Finds the "use pin" text on the Android screen and clicks its center.
        """
        try:
            # Dump UI hierarchy to a file on the device
            subprocess.check_output("adb shell uiautomator dump /sdcard/window_dump_pin.xml", shell=True)
            subprocess.check_output("adb pull /sdcard/window_dump_pin.xml", shell=True)
            with open("window_dump_pin.xml", "r", encoding="utf-8") as f:
                xml_content = f.read()
            # Find node with text="use pin" (case-insensitive)
            match = re.search(r'<node[^>]*text="use pin"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml_content, re.IGNORECASE)
            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                x = (x1 + x2) // 2
                y = (y1 + y2) // 2
                # Tap on the center of the bounds
                subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)
                self.status_label.setText('Status: "Use PIN" tapped')
                # Get PIN from .env file
                # Load PIN from .env using dotenv for reliability
                # sleep for a moment to ensure the tap is registered
                subprocess.run(["sleep", "1"], check=True)
                pin = env_vars.get('PWD')
                if pin:
                    # Tap the PIN on the screen
                    # echo the PIN to terminal for debugging
                    subprocess.run(["adb", "shell", "input", "text", pin], check=True)
                    self.status_label.setText(f'Status: PIN entered')
                    # click enter button
                    subprocess.run(["adb", "shell", "input", "keyevent", "66"], check=True)
                    # QMessageBox.information(self, "PIN Entered", f"PIN '{pin}' has been entered successfully.")
                else:
                    QMessageBox.warning(self, "PIN Not Found", "PIN not found in .env file. Please set the PWD variable.")
                
            else:
                self.status_label.setText('Status: "Use PIN" not found')
                QMessageBox.warning(self, "Not Found", '"use pin" not found on screen.')
            os.remove("window_dump_pin.xml")
            subprocess.run(["adb", "shell", "rm", "/sdcard/window_dump_pin.xml"])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to tap 'use pin': {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())