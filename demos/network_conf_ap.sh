#!/bin/bash -ex

# Configure WLAN interface for AP mode

. wfx_set_env
check_root

INTERFACE="wlan0"
ADDRESS="192.168.51.1/24"

# Tell dhcpcd to release interface
dhcpcd --release "$INTERFACE"

# Set IP configuration
ip addr flush dev "$INTERFACE"
ip addr add "$ADDRESS" dev "$INTERFACE"
ip link set "$INTERFACE" up

# Start DHCP server
killall -w dnsmasq &>/dev/null || true
dnsmasq -C conf/dnsmasq.conf

# Enable ip forward and masquerading
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
