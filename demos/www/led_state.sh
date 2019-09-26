#!/bin/bash
# Copyright (c) 2019, Silicon Laboratories

led_trigger=$( grep -o '\[.*\]' /sys/class/leds/led${1}/trigger )

if [ ${led_trigger} == "[none]" ]; then
    echo 0
else
    echo 1
fi
