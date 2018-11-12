#!/bin/bash

SCRIPT_FOLDER="/home/pi/siliconlabs/wfx_tools/linux_scripts/"
PWD=$(pwd)
cd ${SCRIPT_FOLDER}

all_valid_scripts=$( find -type f | grep wfx )

for script in ${all_valid_scripts}; do 
	script_realpath=$( realpath ${script} )
	basename=$( basename ${script} )
	sudo ln -fs ${script_realpath} /usr/local/bin/${basename}
done

ls -l /usr/local/bin/* --color=auto

cd ${PWD}
