# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# Do not make this script executable, it is to be executed remotely:
# bash <(curl -s https://raw.githubusercontent.com/...)

set -euo pipefail

TOOLS_VERSION="3.2"
COMMON_TOOLS_VERSION="3.2"
DRIVER_VERSION="2.5.2-public"
FIRMWARE_VERSION="FW3.9.0"

GITHUB_TOOLS_PATH="/home/pi/siliconlabs/wfx-linux-tools"
COMMON_TOOLS_PATH="/home/pi/siliconlabs/wfx-common-tools"

if [ $(id -u) == 0 ]; then
    echo "ERROR: running this script as root is not recommended" >&2
    exit 1
fi

repo_checkout_version()
{
    local REPO_PATH=$1
    local VERSION=$2

    STATUS=$(git -C $REPO_PATH status --porcelain --untracked-files=no)
    if ! [ -z "$STATUS" ]; then
        echo "ERROR: the following files where modified in the directory $GITHUB_TOOLS_PATH"
        echo "$STATUS"
        echo "To DISCARD modifications, run \"git reset --hard\" in this directory"
        echo "To SAVE modifications, run \"git stash\" in this directory"
        exit 1
    fi

    git -C $REPO_PATH fetch --all --tags --prune
    if ! git -C $REPO_PATH checkout -q $VERSION; then
        echo "ERROR: cannot get version $VERSION" >&2
        exit 1
    fi
}

set -x

# Update tools
repo_checkout_version $GITHUB_TOOLS_PATH $TOOLS_VERSION
( cd "$GITHUB_TOOLS_PATH"; sudo ./install.sh )
repo_checkout_version $COMMON_TOOLS_PATH $COMMON_TOOLS_VERSION

# Update driver, firmware and PDS
wfx_driver_install --version $DRIVER_VERSION
wfx_firmware_install --version $FIRMWARE_VERSION
wfx_pds_install --auto
