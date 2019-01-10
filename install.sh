#!/bin/bash
# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

set -e

[ $(id -u) != 0 ] && echo "Please run this script as root (running 'sudo $0' should work)" && exit 1 || true
! [ -e install.sh ] && echo "This script must be run from wfx-linux-tools" && exit 1 || true
rm -f /usr/local/bin/wfx_*
rm -f /usr/local/bin/pds_compress

# Create a link under /usr/local/bin for all files matching wfx_ and not containing '.'
for f in $(find -type f -name "wfx_*") pds_compress; do
    b=$(basename $f)
    rp=$(realpath $f)
    if [[ $b != *.* && $b != *~ ]]; then
        set -x
        ln -s $rp /usr/local/bin/$b
        { set +x; } 2>/dev/null # Disable traces without disturbing user
    fi
done

dtc -@ -W no-unit_address_vs_reg overlays/wfx-spi-overlay.dts -o /boot/overlays/wfx-spi.dtbo
dtc -@ -W no-unit_address_vs_reg overlays/wfx-sdio-overlay.dts -o /boot/overlays/wfx-sdio.dtbo

echo "Succes"
