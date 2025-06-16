#!/bin/bash
zenity --warning --text="BE CAREFUL! THIS WILL UNLOCK YOUR PHONE AND ENTER YOUR PASSWORD. MAKE SURE YOU KNOW WHAT YOU ARE DOING!" --width=300 --height=100 --title="Warning" --ok-label="I understand" --no-wrap --timeout=4 

source "$(dirname "$0")/.env"

while true; do
    # Unlock sequence
    adb shell "input keyevent 26"      # Power button (wake up)
    sleep 0.5
    adb shell "input keyevent 82"      # Unlock screen
    adb shell input text "$PWD"        # Enter password
    adb shell input keyevent 66        # Press Enter
    /usr/local/bin/scrcpy -S --window-width=400 --window-height=800

    adb shell "input keyevent 26"

    # Wait for Enter key to lock and repeat
    read -p "Press Enter to unlock again, or Ctrl+C to exit..."

    # Lock the phone (turn screen off)
done