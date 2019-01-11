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

"/home/pi/siliconlabs/wfx-linux-tools/update/wfx_tools_install" 0.23

wfx_fetch
wfx_driver_install --tag 2.0-public
sudo wfx_firmware_install --tag FW2.0.0
sudo wfx_pds_install --model BRD8022A_Rev_A06
