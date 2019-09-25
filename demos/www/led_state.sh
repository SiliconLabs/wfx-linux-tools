#!/bin/bash
# Copyright (c) 2019, Silicon Laboratories

led_trigger=$( cat /sys/class/leds/led${1}/trigger | grep -o '\[.*\]' )

if [ ${led_trigger} == "[none]" ]; then
    echo 0
else
    echo 1
fi
