#!/bin/bash

# This script establishes a connection between an Android device and an Ubuntu system using ADB.
# Usage: ./android_to_ubunto.sh [start|stop]

case "$1" in
    start)
        adb start-server
        adb connect <device_ip_address>  # Replace <device_ip_address> with the actual device IP
        scrcpy &
        echo "ADB connection established and scrcpy started."
        ;;
    stop)
        adb disconnect
        killall scrcpy
        echo "ADB connection terminated and scrcpy closed."
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac