#!/bin/bash
# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# Perform some system configuration when stopping combo demo
# (called by wfx-demo-combo.service)

set -e

# Remove second interface
iw dev wlan1 del

# Disable traffic routing from AP to STA network
echo 0 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -D POSTROUTING -o wlan0 -j MASQUERADE
