#!/bin/bash

set -e

[ $(id -u) != 0 ] && echo "Please run this script as root (running 'sudo $0' should work)" && exit 1 || true
! [ -e install.sh ] && echo "This script must be run from wfx_tools" && exit 1 || true
rm -f /usr/local/bin/wfx_*
rm -f /usr/local/bin/pds_compress

# Create a link under /usr/local/bin for all files matching wfx_ and not containing '.'
for f in $(find -type f -name "wfx_*") pds_compress; do
    b=$(basename $f)
    if [[ $b != *.* && $b != *~ ]]; then
        ln -s $(realpath ${f}) /usr/local/bin/$b
    fi
done

# wfx_overlay_compile linux_overlays/wfx-spi-overlay.dts linux_overlays/wfx-sdio-overlay.dts
install -m 644 linux_overlays/wfx-spi.dtbo /boot/overlays/
install -m 644 linux_overlays/wfx-sdio.dtbo /boot/overlays/
