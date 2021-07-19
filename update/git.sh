#!/bin/bash
# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

set -euo pipefail
. wfx_set_env
check_not_root

USAGE="Usage: $(basename $0) --path PATH [--url URL] OPTION

WARNING: This tool is meant to be used by other tools only.
It is a wrapper for git to handle specific use cases.

Options:
  --help          display this message
  --path PATH     git repo path
  --url URL       git repo url
  --list-tags     list tags on all remotes
  --version VER   checkout VER on repo
"

REPO_PATH=""
REPO_URL=""
VERSION=""
MODE=""

[ $# -eq 0 ] && error
LONGOPTS="help,path:,url:,list-tags,version:"
! PARSED=$(getopt --options="" --longoptions=$LONGOPTS --name "$0" -- "$@")
[[ ${PIPESTATUS[0]} -ne 0 ]] && error
eval set -- "$PARSED"
while true; do
    case "$1" in
        --path)      REPO_PATH="$2";    shift ;;
        --url)       REPO_URL="$2";     shift ;;
        --list-tags) MODE="list";             ;;
        --version)   MODE="version"; VERSION="$2"; shift ;;
        --help)      echo "$USAGE"; exit 0 ;;
        --)          shift; break ;;
        *)           error ;;
    esac
    shift
done
[ $# -ne 0 ] && error
[ -z "$REPO_PATH" ] && error

GIT="git -C $REPO_PATH"

if [ ! -d "$REPO_PATH" ]; then
    [ -z "$REPO_URL" ] && echo "ERROR: repo url is needed to clone" >&2 && exit 1
    git clone "$REPO_URL" "$REPO_PATH"
fi

case "$MODE" in
    list)
        SUCCESS=true
        for REMOTE in $($GIT remote); do
            echo "Tags on remote $REMOTE ($($GIT remote -v | grep fetch | grep $REMOTE | cut -f2 | sed -nr 's%.*((://)|@)([^/:]*).*%\3%p'
)):"
            if ! $GIT ls-remote --tags "$REMOTE" 2>/dev/null | sed -nre 's%.*refs/tags/(.*)%\1%p' | sort -V; then
                SUCCESS=false
                break
            fi
            echo ""
        done
        if [ "$SUCCESS" = "false" ]; then
            echo "WARNING: cannot get tags from remote, listing local tags:"
            $GIT tag -l
        fi
        ;;
    version)
        [ -z "$VERSION" ] && echo "ERROR: version is mandatory" >&2 && exit 1
        check_working_clean $REPO_PATH
        # Fetch only when unknown version or branch from remote
        if ! $GIT checkout -q "$VERSION" 2>/dev/null ||
                $GIT branch --list --remote | grep -q "$VERSION"; then
            $GIT fetch --all --tags --prune --force
            if ! $GIT checkout -q "$VERSION"; then
                echo "ERROR: cannot find version" >&2
                exit 1
            fi
        fi
        ;;
    *)
        error
        ;;
esac
