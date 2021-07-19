#!/bin/bash
# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# Perform some system configuration before launching combo demo
# (called by wfx-demo-combo.service)

set -e

# Allow web server access to LEDs
chmod g+rw /sys/class/leds/led{0,1}/{trigger,brightness}
chown :netdev /sys/class/leds/led{0,1}/{trigger,brightness}

# Start second interface for access point
iw dev wlan0 interface add wlan1 type managed

# IP configuration of AP interface
/sbin/dhcpcd --release wlan1
ip addr add 10.10.0.1/24 dev wlan1
