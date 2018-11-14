#!/bin/bash -ex

# Start a demo in station mode for browsing

. wfx_set_env
check_root

INTERFACE="wlan0"
# TODO: write wpa_supplicant.conf
WPA_SUPPLICANT_CONF=$SILABS_ROOT/wfx_tools/demos/conf/wpa_supplicant.conf

# Check wlan0
if ! ip link show "$INTERFACE" &> /dev/null; then
    >&2 echo "Interface $INTERFACE not detected, exiting"
    exit 1
fi

# Kill potentially started process
kill_check wpa_supplicant hostapd dnsmasq

# Start wpa_supplicant
wpa_supplicant -i "$INTERFACE" -c "$WPA_SUPPLICANT_CONF" -B

# Tell dhcpcd to control WLAN interface
dhcpcd --rebind "$INTERFACE"

# TODO: Start wpagui
# TODO: check that we have a screen
# TODO: check if we need to disable lxpanel (on generated image)
