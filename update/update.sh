# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# This script is to be executed with curl:
# bash <(curl -s https://raw.githubusercontent.com/...)

set -euo pipefail

if [ $(id -u) == 0 ]; then
    echo "ERROR: running this script as root is not recommended" >&2
    exit 1
fi

set -x

export TOOLS_VERSION="origin/SD3"

# Install tools
export GITHUB_TOOLS_PATH="/home/pi/siliconlabs/wfx-linux-tools"
git -C $GITHUB_TOOLS_PATH fetch --all --tags --prune
git -C $GITHUB_TOOLS_PATH show $TOOLS_VERSION:update/tools_install.sh | bash -s

# Install driver, firmware and PDS
wfx_driver_install --version 2.2.5-public
wfx_firmware_install --version FW3.3.1
wfx_pds_install --auto
