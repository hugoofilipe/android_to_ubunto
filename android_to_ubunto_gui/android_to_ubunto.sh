#!/bin/bash

# Usage: ./android_to_ubunto.sh [start|stop|wakeup]
source "$(dirname "$0")/../.env"

case "$1" in
    start)
        adb start-server
        adb connect "$DEVICE_IP"
        # Unlock sequence
        adb shell "input keyevent 26"      # Power button (wake up)
        sleep 0.5
        adb shell "input keyevent 82"      # Unlock screen
        adb shell input text "$PWD"        # Enter password
        adb shell input keyevent 66        # Press Enter
        # /usr/local/bin/scrcpy -S --window-width=554 --window-height=1200 
        /usr/local/bin/scrcpy -S  
        ;;
    stop)
        adb shell "input keyevent 26"
        killall scrcpy
        pkill -f adb
        echo "scrcpy closed and adb killed."
        ;;
    wakeup)
        adb shell "input keyevent 223"
        sleep 0.5
        adb shell "input keyevent 224"
        sleep 0.5
        adb shell "input keyevent 82"
        adb shell input text "$PWD"
        adb shell input keyevent 66
        ;;
    *)
        echo "Usage: $0 {start|stop|wakeup}"
        exit 1
        ;;
esac