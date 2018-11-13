#!/bin/bash -ex

# Start an access point

. wfx_set_env
check_root

check_no_process wpa_supplicant
check_no_process hostapd
check_no_process dhcpcd

INTERFACE="wlan0"
ADDRESS="192.168.51.1/24"

# TODO: check if wpa_supplicant or hostapd or dnsmasq need to be stopped

# Tell dhcpcd to release interface
dhcpcd --release "$INTERFACE"

# Set static IP configuration
ip addr flush dev "$INTERFACE"
ip addr add "$ADDRESS" dev "$INTERFACE"
ip link set "$INTERFACE" up

# Start DHCP server
dnsmasq -C conf/dnsmasq.conf

# Start hostapd
hostapd -B conf/hostapd.conf

# Enable ip forward and masquerading
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
