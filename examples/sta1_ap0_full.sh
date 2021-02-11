#!/bin/bash
# Starting a STA on wlan1 then an AP on wlan0

STA_SSID="HOME_AP"
STA_PASSWORD="HOME_AP_PASSWORD"

SOFTAP_SSID="MY_SOFTAP_SSID"
SOFTAP_PASSWORD="MY_SOFTAP_PASSWORD"

STA_INTERFACE="wlan1"
SOFTAP_INTERFACE="wlan0"

SOFTAP_IP="192.168.12.1"

COUNTRY=FR

# Clean the WiFi setup
sudo killall wpa_supplicant
sudo killall hostapd
sudo killall dnsmasq
wfx_driver_reload -C

# Fill SoftAP configuration
cat > hostapd.conf << EOF
interface=${SOFTAP_INTERFACE}
driver=nl80211
ctrl_interface=/var/run/hostapd
ctrl_interface_group=netdev

ssid=${SOFTAP_SSID}
wpa_passphrase=${SOFTAP_PASSWORD}

wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP

country_code=${COUNTRY}
channel=6

auth_algs=1
hw_mode=g
ieee80211n=1
dtim_period=1
beacon_int=100
max_num_sta=8
ieee80211w=1
EOF

# Fill STA configuration
cat > wpa_supplicant.conf << EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=0
country=${COUNTRY}

network={
	ssid="${STA_SSID}"
	key_mgmt=WPA-PSK
	psk="${STA_PASSWORD}"
}
EOF

set -ex
# Add wlan1 interface on wlan0 device
sudo iw dev wlan0 interface add wlan1 type managed
# The following' ip link set dev wlan0 down' line is required to avoid this error:
#  'Failed to connect to non-global ctrl_ifname: wlan1 error: No such file or directory'
# Somehow, this happens because we're starting the STA on wlan1 first
# It looks like a bug, since 'sudo ip link show' indicates that wlan0 is already DOWN...
sudo ip link set dev wlan0 down

# Wait (max 10 sec) for the STA interface to be different from 'DORMANT' or 'UNKNOWN'
set +ex
for (( n=1; n<=10; n++ )); do
	state=$(sudo ip link show ${STA_INTERFACE} | grep -oE "state \w*")
	echo "${STA_INTERFACE} ${state}"
	if ! echo "${STA_INTERFACE} ${state}" | grep -E "DORMANT|UNKNOWN" >/dev/null ; then
        break
    fi
    sleep 1
done
set -x

# Start the STA
sudo /sbin/wpa_supplicant -i ${STA_INTERFACE} -Bst -c wpa_supplicant.conf

# Wait (max 10 sec) for the SOFTAP interface to be different from 'DORMANT' or 'UNKNOWN'
set +ex
for (( n=1; n<=10; n++ )); do
	state=$(sudo ip link show ${SOFTAP_INTERFACE} | grep -oE "state \w*")
	echo "${SOFTAP_INTERFACE} ${state}"
	if ! echo "${SOFTAP_INTERFACE} ${state}" | grep -E "DORMANT|UNKNOWN" ; then
        break
    fi
    sleep 1
done
set -x

# Start the SoftAP
sudo /usr/sbin/hostapd -B hostapd.conf

# Start DHCP and DNS on softAP interface
set +x
RANGE="${SOFTAP_IP%.*}.100,${SOFTAP_IP%.*}.200"
set -x
sudo dnsmasq --conf-file=/dev/null --interface="$SOFTAP_INTERFACE" --bind-interfaces --except-interface=lo --dhcp-range="$RANGE"

# Wait (max 10 sec) for the STA to obtain an IP address
set +ex
echo ""
for (( n=1; n<=10; n++ )); do
	state=$(/sbin/wpa_cli status | grep -E "ip_address")
	if echo "${STA_INTERFACE} ${state}" | grep -E "ip_address" ; then
        break
    fi
    sleep 1
done

# Print STA status
printf "\nSTA: "
/sbin/wpa_cli status | grep -E "interface|^ssid|state|ip_address"
state=$(sudo ip link show ${STA_INTERFACE} | grep -oE "state \w*")
echo "${STA_INTERFACE} ${state}"

# Print SoftAP status
printf "\nAP: "
/usr/sbin/hostapd_cli status | grep -E "interface|ssid|state"
state=$(sudo ip link show ${SOFTAP_INTERFACE} | grep -oE "state \w*")
echo "${SOFTAP_INTERFACE} ${state}"
