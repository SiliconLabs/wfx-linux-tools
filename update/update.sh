# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# This script is to be executed with curl:
# bash <(curl -s https://raw.githubusercontent.com/...)

set -e

if [ $(id -u) == 0 ]; then
    echo "ERROR: running this script as root is not recommended" >&2
    exit 1
fi

set -x

"/home/pi/siliconlabs/wfx-linux-tools/update/wfx_tools_install" 2.2_RC8

wfx_driver_install --version 2.1.2-public
wfx_firmware_install --version dd919f618cba4ada4c63779e0c83d3c263ce8381
sudo wfx_pds_install --auto
