# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# Do not make this script executable, it is to be executed remotely:
# bash <(curl -s https://raw.githubusercontent.com/...)

set -euo pipefail

TOOLS_VERSION="origin/SD3"
DRIVER_VERSION="2.2.5-public"
FIRMWARE_VERSION="FW3.3.1"

if [ $(id -u) == 0 ]; then
    echo "ERROR: running this script as root is not recommended" >&2
    exit 1
fi

set -x

# Update tools
GITHUB_TOOLS_PATH="/home/pi/siliconlabs/wfx-linux-tools"
GIT="git -C $GITHUB_TOOLS_PATH"

STATUS=$($GIT status --porcelain --untracked-files=no)
if ! [ -z "$STATUS" ]; then
    echo "ERROR: the following files where modified in the directory $GITHUB_TOOLS_PATH"
    echo "$STATUS"
    echo "To DISCARD modifications, run \"git reset --hard\" in this directory"
    echo "To SAVE modifications, run \"git stash\" in this directory"
    exit 1
fi

$GIT fetch --all --tags --prune
if ! $GIT checkout -q $TOOLS_VERSION; then
    echo "ERROR: cannot get version $TOOLS_VERSION" >&2
    exit 1
fi

# Launch updated tools install script
( cd "$GITHUB_TOOLS_PATH"; sudo ./install.sh )


# Update driver, firmware and PDS
wfx_driver_install --version $DRIVER_VERSION
wfx_firmware_install --version $FIRMWARE_VERSION
wfx_pds_install --auto
