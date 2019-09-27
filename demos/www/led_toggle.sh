#!/bin/bash
# Copyright (c) 2019, Silicon Laboratories
# led_toggle <0/1>             toggles the led

# As from the Raspberry Pi documentation, toggling the LEDs
#  Should be possible by setting the trigger to 'none'
#   & changing the brigthness value from 0 to 255
# But this doesn't work reliably.
# Changing the trigger from 'none' (with brightness at 0)
#  to 'default-on' works, though
#

led_trigger=$( grep -o '\[.*\]' /sys/class/leds/led${1}/trigger )

if [ ${led_trigger} == "[none]" ]; then
    echo default-on > /sys/class/leds/led${1}/trigger
else
    echo none       > /sys/class/leds/led${1}/trigger
    echo 0          > /sys/class/leds/led${1}/brightness
fi
