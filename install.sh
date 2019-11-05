#!/bin/bash
# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# This script performs actions needed to install public tools
# It is typically ran by tools_install.sh after an update

set -e
# Always run as root
[ $(id -u) = 0 ] || exec sudo $0 "$@"

! [ -e install.sh ] && echo "This script must be run from wfx-linux-tools" && exit 1 || true

rm -f /usr/local/bin/wfx_*
rm -f /usr/local/bin/pds_compress

# Create a link under /usr/local/bin for all files matching wfx_ (ignore files with extension and backup files)
find ! -path '*/\.*' -type f \( -name 'wfx_*' -o -name pds_compress \) ! -name '*~' ! -name '*.*' -execdir bash -c 'ln -vs $(realpath {}) /usr/local/bin/$(basename {})' \;

# Disable power save for best performance
UDEV_FILE=/etc/udev/rules.d/80-wifi-powersave.rules
UDEV_RULE='ACTION=="add", SUBSYSTEM=="net", KERNEL=="wl*", DRIVERS=="wfx-*", RUN+="/sbin/iw dev $name set power_save off"'
[ -f $UDEV_FILE ] || echo "$UDEV_RULE"  | sudo tee $UDEV_FILE >/dev/null

# Allow IP forward to enable wfx_ap --forward (it is still needed to enable it with sysctl)
perl -i.old -p0e 's/-P FORWARD DROP/-P FORWARD ACCEPT/igs' /etc/iptables/rules.v4

# Allow traffic from all Ethernet interfaces
perl -i -p0e 's/-A INPUT -i eth0 -j ACCEPT\n-A INPUT -i eth1 -j ACCEPT/-A INPUT -i eth+ -j ACCEPT/igs' /etc/iptables/rules.v4

# Allow DHCP server on all interfaces instead of only wlan1
perl -i -p0e 's/# Allow DHCP server for wfx-demo-combo\n-A INPUT -i wlan1 -p udp --dport 67:68 --sport 67:68 -j ACCEPT/# Allow DHCP server\n-A INPUT -p udp --dport 67:68 --sport 67:68 -j ACCEPT/igs' /etc/iptables/rules.v4

# Allow DNS
perl -i -p0e 's/(-A INPUT -p tcp -m tcp --dport http -j ACCEPT\n)(\n# Allow iperf and iperf3)/$1\n# Allow DNS server\n-A INPUT -p udp --dport 53 -j ACCEPT\n$2/igs' /etc/iptables/rules.v4

# Disable wpa_supplicant launched by systmed to avoid conflict with demo/tests
systemctl disable wpa_supplicant.service

cat << EOF | tee /etc/sudoers.d/020_wfx-demo
# Allow wfx demo webpage to start/stop STA/AP
Cmnd_Alias WEBAPP = /bin/systemctl start wfx-demo-hostapd.service,\
                    /bin/systemctl stop  wfx-demo-hostapd.service,\
                    /bin/systemctl start wfx-demo-wpa_supplicant.service,\
                    /bin/systemctl stop  wfx-demo-wpa_supplicant.service

%netdev ALL=(ALL) NOPASSWD: WEBAPP
EOF
chown 0440 /etc/sudoers.d/020_wfx-demo

dtc -@ -W no-unit_address_vs_reg overlays/wfx-spi-overlay.dts -o /boot/overlays/wfx-spi.dtbo
dtc -@ -W no-unit_address_vs_reg overlays/wfx-sdio-overlay.dts -o /boot/overlays/wfx-sdio.dtbo
dtc -@ -W no-unit_address_vs_reg overlays/spidev-overlay.dts -o /boot/overlays/spidev.dtbo
dtc -@ -W no-unit_address_vs_reg overlays/disable-uart-overlay.dts -o /boot/overlays/disable-uart.dtbo

echo "Success"
