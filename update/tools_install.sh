#!/bin/bash
# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

set -ex

GITHUB_TOOLS_PATH="/home/pi/siliconlabs/wfx-linux-tools"
GITHUB_TOOLS_INTERNAL_PATH="$GITHUB_TOOLS_PATH/internal"

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "ERROR: version needed" >&2
    exit 1
fi

if [ $# -gt 0 ]; then
    STATUS=$(git -C $GITHUB_TOOLS_PATH status --porcelain --untracked-files=no)
    if ! [ -z "$STATUS" ]; then
	echo "ERROR: the following files where modified in the direcory $REPO_PATH"
	echo "$STATUS"
	echo "To DISCARD modifications, run \"git reset --hard\" in this directory"
	echo "To SAVE modifications, run \"git stash\" in this directory"
	exit 1
    fi

    if ! git -C $GITHUB_TOOLS_PATH checkout $1; then
        echo "ERROR: cannot get version $1" >&2
        echo "Possible tags:"
        git -C $GITHUB_TOOLS_PATH tag | sed 's/^/  /'
        exit 1
    fi
fi

# Update internal tools (ignore if file does not exist)
STATUS=0
$GITHUB_TOOLS_INTERNAL_PATH/install_internal.sh || STATUS=$?
if [ $STATUS != 0 ] && [ $STATUS != 127 ]; then
    exit 1
fi

( cd "$GITHUB_TOOLS_PATH"; sudo ./install.sh )
