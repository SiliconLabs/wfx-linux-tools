# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# This script is to be executed with curl:
# bash <(curl -s https://raw.githubusercontent.com/...)

set -e

if [ $(id -u) == 0 ]; then
    echo "ERROR: running this script as root is not recommended" >&2
    exit 1
fi

export GITHUB_TOOLS_PATH="/home/pi/siliconlabs/wfx-linux-tools"

set -x

"$GITHUB_TOOLS_PATH/update/wfx_tools_install" 0.4

wfx_fetch
wfx_driver_install 1.6-public
sudo wfx_firmware_install FW1.2.15
sudo wfx_pds_install BRD8022A_Rev_A05.pds.in
