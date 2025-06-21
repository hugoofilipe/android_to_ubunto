# android_to_ubunto
This repository contains a script to stablish a connection between an Android device and an Ubuntu system using ADB (Android Debug Bridge). 
with this script, you can easily connect your Android device to your Ubuntu system and execute commands on the device.
Also, it provides a simple way to see the device's screen on your Ubuntu system.

## Requirements
- `adb` installed on your Ubuntu system.
- `srccpy` installed on your Ubuntu system.
- `zenity` installed on your Ubuntu system.
- An Android device with USB debugging enabled.

## Installation
1. Install `adb`, `srccpy`, and `zenity` if they are not already installed:
   ```bash
   sudo apt update
   sudo apt install adb scrcpy zenity
   ```
2. Clone the repository:
   ```bash
   git clone git@github.com:hugoofilipe/android_to_ubunto.git
   ```
3. Create an env file in the cloned directory:
   ```bash
    cd android_to_ubunto
    touch .env
   ```
4. Open the `.env` file and add the following line:
   ```bash
   PWD=<your_password>  
   ```

## Usage
1. Connect your Android device to your Ubuntu system via USB.
2. Make sure USB debugging is enabled on your Android device.
3. Run the script:
   ```bash
   ./android_to_ubunto.sh
   ```
4. Follow the prompts to select the desired action (connect, disconnect, or exit).
5. If you choose to connect, the script will establish an ADB connection and start `scrcpy` to display your Android device's screen on your Ubuntu system.
6. If you choose to disconnect, the script will terminate the ADB connection and close `scrcpy`.
