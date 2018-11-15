#!/bin/bash -ex

# Start a demo in access point mode with a local web server

. wfx_set_env
check_root

INTERFACE="wlan0"
ADDRESS="192.168.51.1/24"
DNSMASQ_CONF=$GITHUB_TOOLS_PATH/demos/conf/dnsmasq.conf
HOSTAPD_CONF=$GITHUB_TOOLS_PATH/demos/conf/hostapd.conf

# Check wlan0
if ! ip link show "$INTERFACE" &> /dev/null; then
    echo "Interface $INTERFACE not detected, exiting" >&2
    exit 1
fi

# Try to stop a potentially running wpa_supplicant
wpa_cli -i "$INTERFACE" terminate 2>/dev/null || true

# Kill potentially started process
kill_check wpa_supplicant hostapd wpa_gui
kill $(cat /var/run/dnsmasq-wlan0.pid) || true

# TODO: find a better way
sleep 1

# Tell dhcpcd to release WLAN interface
dhcpcd --release "$INTERFACE"

# Set static IP configuration
ip addr flush dev "$INTERFACE"
ip addr add "$ADDRESS" dev "$INTERFACE"
ip link set "$INTERFACE" up

# Start DHCP server
dnsmasq -C "$DNSMASQ_CONF"

# Start hostapd
# TODO: check why hostapd sometimes fails to restart (wlan0 busy)
hostapd -B "$HOSTAPD_CONF"

# TODO: start HTTP server with a static page

# To allow traffic forwarding to a gateway, uncomment the following lines
#echo 1 > /proc/sys/net/ipv4/ip_forward
#iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
