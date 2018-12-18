# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# This script is to be executed with curl:
# bash <(curl -s https://raw.githubusercontent.com/...)

set -e

. wfx_set_env
check_no_root

set -x

"$GITHUB_TOOLS_PATH/update/wfx_tools_install" 0.2
wfx_driver_install 1.6-public
sudo wfx_firmware_install FW1.2.15
sudo wfx_pds_install BRD8022A_Rev_A05.pds.in
