#!/bin/bash
# Copyright (c) 2019, Silicon Laboratories

wpa_cli scan >/dev/null
sleep 1
wpa_cli scan_results | grep -o -E '^([[:xdigit:]]{2}:){5}.*$'
