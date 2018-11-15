#!/bin/bash -ex

# Start a demo in station mode for browsing

. wfx_set_env
check_no_root

INTERFACE="wlan0"
WPA_SUPPLICANT_CONF=$SILABS_ROOT/wfx_tools/demos/conf/wpa_supplicant.conf

# Check wlan0
if ! ip link show "$INTERFACE" &> /dev/null; then
    >&2 echo "Interface $INTERFACE not detected, exiting"
    exit 1
fi

# Try to stop a potentially running wpa_supplicant (then wait for termination)
wpa_cli -i "$INTERFACE" terminate 2>/dev/null && sleep 1 || true

# Kill potentially started process
sudo bash -c '. wfx_set_env; kill_check wpa_supplicant hostapd dnsmasq wpa_gui'

# Tell dhcpcd to control WLAN interface (in case of previous demo_AP)
sudo dhcpcd --rebind "$INTERFACE"

# Start wpa_supplicant
sudo wpa_supplicant -i "$INTERFACE" -c "$WPA_SUPPLICANT_CONF" -B -s

# TODO: Start wpagui
wpa_gui &
# TODO: check that we have a screen
