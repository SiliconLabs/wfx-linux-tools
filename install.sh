#!/bin/bash

SCRIPT_FOLDER="/home/pi/siliconlabs/wfx_tools/linux_scripts/"
PWD=$(pwd)
cd ${SCRIPT_FOLDER}

all_valid_scripts=$( find -type f | grep wfx_ )

rm -f /usr/local/bin/wfx_*

# Create a link under /usr/local/bin for all files matching wfx_ and not containing '.'
for script in ${all_valid_scripts}; do 
	script_realpath=$( realpath ${script} )
	basename=$( basename ${script} )
	dot_test=$( echo {$basename} | grep "." )
	if [ "${dot_test}" != "" ]; then
	    ln -fs ${script_realpath} /usr/local/bin/${basename}
	fi
done

ls -l /usr/local/bin/* --color=auto

cd ${PWD}
