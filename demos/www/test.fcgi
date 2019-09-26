#!/usr/bin/python3
import time
import os

from flup.server.fcgi import WSGIServer
import json

from cgi_commons import bash_res
import collections

def read_led_state(led_nb):
    f = open(f'/sys/class/leds/led{led_nb}/trigger')
    if '[none]' in f.read():
        return 0
    else:
        return 1

def myapp(environ, start_response):
    # We use collections.OrderedDict() instead of dict() because
    #  the web page refers to the json content as info[n].state,
    #  n being hardcoded as follows
    #  info[0]-> LED0
    #  info[1]-> LED1
    #  info[2]-> Connection (must be 'Connected' or 'Not Connected')
    #  info[3]-> STA_IP_address
    # As a consequence, the order of the following lines is FIXED
    try:
        start_response('200 OK', [('Content-Type', 'text/plain')])

        state=collections.OrderedDict()
        AP_IF  = "wlan1"
        STA_IF = "wlan0"
        state["LED0"] = read_led_state(0)
        state["LED1"] = read_led_state(1)
        state["Connection"] = bash_res("wpa_cli status | grep wpa_state | cut -d '=' -f 2")
        STA_ssid = "SSID"
        STA_ssid = bash_res("wpa_cli status | grep ^ssid | cut -d '=' -f 2")
        if "COMPLETED" in state["Connection"]:
            state["Connection"] = "STA Connected to " + STA_ssid
        else:
            state["Connection"] = "Not Connected"
        state["STA_IP_address"] = bash_res("ip addr show " + STA_IF + " | grep 'global' | grep 'wlan' | grep 'inet '| cut -d '/' -f 1 | cut -d ' ' -f 6")
        # Additional state values (initially not visible in the web page)
        state["AP_IP_address"]  = bash_res("ip addr show " + AP_IF  + " | grep 'global' | grep 'wlan' | grep 'inet '| cut -d '/' -f 1 | cut -d ' ' -f 6")
        state["AP_ssid"] = bash_res("hostapd_cli status | grep ^ssid | cut -d '=' -f 2")
        state["wpa_cli"] = bash_res("wpa_cli status | grep wpa_state | cut -d '=' -f 2")
        values=list()

        for s in state.keys():
            value=collections.OrderedDict()
            value["name"]=s
            value["state"]=state[s]
            values.append(value)

        json_string=json.dumps(values, separators=(',', ':'))
        
        return json_string
        
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    WSGIServer(myapp, bindAddress='/tmp/fcgi.sock-0').run()
