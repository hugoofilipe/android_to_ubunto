# android_to_ubunto

This repository contains scripts and a GUI application to establish a connection between an Android device and an Ubuntu system using ADB (Android Debug Bridge).  
With this project, you can easily connect your Android device to your Ubuntu system, execute commands, and view your device's screen.

---

## Requirements

- `adb` installed on your Ubuntu system.
- `scrcpy` installed on your Ubuntu system.
- `zenity` installed on your Ubuntu system.
- `uxplay` installed on your Ubuntu system (for iPad mirroring).
- Python 3 (recommended: 3.8+)
- `pip` for Python 3
- PyQt5 Python package
- An Android device with USB debugging enabled.

---

## Installation

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install adb scrcpy zenity python3 python3-pip
   # For iPad mirroring
   sudo snap install uxplay
   ```

2. **Clone the repository:**
   ```bash
   git clone git@github.com:hugoofilipe/android_to_ubunto.git
   cd android_to_ubunto
   ```

3. **Create an env file in the cloned directory:**
   ```bash
   touch .env
   ```
   Add your device password to `.env`:
   ```bash
   PWD=<your_password>
   ```

4. **Install Python dependencies:**
   ```bash
   cd android_to_ubunto_gui
   pip3 install -r requirements.txt
   ```

---

## Building the Executable (Optional)

If you want a standalone executable for the GUI:

1. **Install PyInstaller:**
   ```bash
   pip3 install pyinstaller
   ```

2. **Build the executable:**
   ```bash
   cd android_to_ubunto_gui/src
   pyinstaller --onefile --windowed main.py --name android_to_ubunto
   ```
   The executable will be created in the `dist/` folder.

---

## Creating a Desktop Shortcut (Ubuntu App Menu Icon)

1. **(Optional) Add an icon:**  
   Place a PNG icon (e.g., `icon.png`) in `android_to_ubunto_gui/`.

2. **Create a desktop entry:**
   ```bash
   nano ~/.local/share/applications/android_to_ubunto.desktop
   ```
   Paste the following (update paths as needed):

   ```
   [Desktop Entry]
   Name=Android to Ubuntu
   Comment=Unlock and control your Android device from Ubuntu
   Exec=/home/hugoofilipe/drive/projects/tools_on_linux/repos/android_to_ubunto/android_to_ubunto_gui/src/dist/android_to_ubunto
   Icon=/home/hugoofilipe/drive/projects/tools_on_linux/repos/android_to_ubunto/android_to_ubunto_gui/icon.png
   Terminal=false
   Type=Application
   Categories=Utility;
   ```

3. **Make the desktop file executable:**
   ```bash
   chmod +x ~/.local/share/applications/android_to_ubunto.desktop
   ```

4. **Update the desktop database:**
   ```bash
   update-desktop-database ~/.local/share/applications
   ```

5. **Find your app:**  
   Search for "Android to Ubuntu" in your Ubuntu app menu.  
   You can right-click and "Add to Favorites" for quick access.

---

## Usage

### Script Mode

1. Connect your Android device to your Ubuntu system via USB.
2. Make sure USB debugging is enabled on your Android device.
3. Run the script:
   ```bash
   ./adb_unlock.sh
   ```

### GUI Mode

1. Run the GUI:
   ```bash
   cd android_to_ubunto_gui/src
   python3 main.py
   ```
   Or, if you built the executable:
   ```bash
   ./dist/android_to_ubunto
   ```
2. Use the GUI window to:
   - Start/stop the unlock script for your Android device.
   - **Turn On/Off iPad**: This will run or kill the `uxplay -avdec -vs ximagesink` process for iPad mirroring.

---

## Project Structure

```
android_to_ubunto/
├── .env
├── adb_unlock.sh
├── android_to_ubunto.sh
├── README.md
└── android_to_ubunto_gui/
    ├── requirements.txt
    ├── icon.png
    ├── src/
    │   ├── main.py
    │   └── gui.py
    └── dist/
        └── android_to_ubunto
```

---

## Notes

- Make sure `adb_unlock.sh` is executable:  
  ```bash
  chmod +x adb_unlock.sh
  ```
- The `.env` file must be present and contain your device password as `PWD=<your_password>`.
- The GUI launches and terminates the unlock script as a subprocess.
- The "Turn On/Off iPad" button in the GUI will start or kill the `uxplay` process for iPad mirroring.  
  Make sure `uxplay` is installed and available in your PATH.

---

**Enjoy controlling your Android and iPad devices from Ubuntu!**
