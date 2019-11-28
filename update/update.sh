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

"/home/pi/siliconlabs/wfx-linux-tools/update/wfx_tools_install" origin/SD3

wfx_driver_install --version 2.2.5-public
fx_firmware_install --version FW3.3.0
wfx_pds_install --auto
