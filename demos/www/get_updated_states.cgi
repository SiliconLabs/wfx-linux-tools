#!/usr/bin/python
from cgi_commons import *

import json

def main():
    # We use collections.OrderedDict() instead of dict() because
    #  the web page refers to the json content as info[n].state,
    #  n being hardcoded as follows
    #  info[0]-> LED0
    #  info[1]-> LED1
    #  info[2]-> Connection (must be 'Connected' or 'Not Connected')
    #  info[3]-> STA_IP_address
    # As a consequence, the order of the following lines is FIXED
    state=collections.OrderedDict()
    AP_IF  = "wlan1"
    STA_IF = "wlan0"
    state["LED0"] = bash_res("./led_state.sh 0")
    state["LED1"] = bash_res("./led_state.sh 1")
    state["Connection"] = bash_res("wpa_cli status | grep wpa_state | cut -d '=' -f 2")
    if state["Connection"] == "COMPLETED":
        state["Connection"] = "Connected"
    if state["Connection"] == "DISCONNECTED":
        state["Connection"] = "Not Connected"
    state["STA_IP_address"] = bash_res("ip addr show " + STA_IF + " | grep 'global' | grep 'wlan' | grep 'inet '| cut -d '/' -f 1 | cut -d ' ' -f 6")
    # Additional state values (initially not visible in the web page)
    state["AP_IP_address"]  = bash_res("ip addr show " + AP_IF  + " | grep 'global' | grep 'wlan' | grep 'inet '| cut -d '/' -f 1 | cut -d ' ' -f 6")
    state["AP_ssid"]  = bash_res("hostapd_cli status | grep ^ssid | cut -d '=' -f 2")
    state["STA_ssid"] = bash_res("wpa_cli status | grep ^ssid | cut -d '=' -f 2")

    profile("all_done", 1)
    state["Profiling"] = str(profiling)
    values=list()

    for s in state.keys():
        value=collections.OrderedDict()
        value["name"]=s
        value["state"]=state[s]
        values.append(value)

    json_string=json.dumps(values, separators=(',', ':'))
    print(json_string)
    # dmesg_print(json_string)


if __name__=="__main__":
    main()
