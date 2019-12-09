#!/bin/bash
# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

# DO NOT MOVE THIS SCRIPT OR MAKE IT EXECUTABLE
# this script is to be run by update.sh
#
# This second stage is designed just to update wfx-linux-tools code
# The installation itself is then delegated to install.sh

set -ex

GIT="git -C $GITHUB_TOOLS_PATH"

if [ -z "$TOOLS_VERSION" ]; then
    echo "ERROR: version needed" >&2
    exit 1
fi

STATUS=$($GIT status --porcelain --untracked-files=no)
if ! [ -z "$STATUS" ]; then
    echo "ERROR: the following files where modified in the directory $REPO_PATH"
    echo "$STATUS"
    echo "To DISCARD modifications, run \"git reset --hard\" in this directory"
    echo "To SAVE modifications, run \"git stash\" in this directory"
    exit 1
fi

if ! $GIT checkout -q $TOOLS_VERSION; then
    echo "ERROR: cannot get version $TOOLS_VERSION" >&2
    exit 1
fi

# Launch updated install script
( cd "$GITHUB_TOOLS_PATH"; sudo ./install.sh )
