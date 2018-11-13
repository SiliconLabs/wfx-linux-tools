#!/bin/bash -ex

# Configure WLAN interface for access point mode

. wfx_set_env
check_root

INTERFACE="wlan0"
ADDRESS="192.168.51.1/24"
DNSMASQ_CONF=$SILABS_ROOT/wfx_tools/demos/conf/dnsmasq.conf
HOSTAPD_CONF=$SILABS_ROOT/wfx_tools/demos/conf/hostapd.conf

# Check wlan0
if ! ip link show "$INTERFACE" &> /dev/null; then
    >&2 echo "Interface $INTERFACE not detected, exiting"
    exit 1
fi

# Kill potentially started process
kill_check wpa_supplicant hostapd dnsmasq

# Tell dhcpcd to release WLAN interface
dhcpcd --release "$INTERFACE"

# Set static IP configuration
ip addr flush dev "$INTERFACE"
ip addr add "$ADDRESS" dev "$INTERFACE"
ip link set "$INTERFACE" up

# Start DHCP server
dnsmasq -C "$DNSMASQ_CONF"

# Start hostapd
hostapd -B "$HOSTAPD_CONF"

# Enable ip forward and masquerading
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
