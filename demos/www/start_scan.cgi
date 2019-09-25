#!/usr/bin/python
from cgi_commons import *

import sys
import json
import collections


def main():
    # We use collections.OrderedDict() instead of dict() because
    #  the web page refers to the json content as info[n].state,
    #  n being hardcoded as follows
    #  info[0]-> LED0
    #  info[1]-> LED1
    #  info[2]-> Connection
    #  info[3]-> IP_address
    # As a consequence, the order of the following lines is FIXED
    scan_result = bash_res("./start_scan.sh")

    values=list()

    rssis=collections.OrderedDict()
    secus=collections.OrderedDict()

    for line in scan_result.split("\n"):
        line_len = len(line.split())
        if line_len == 5:
            (MAC, freq , rssi, secu, ssid) = line.split()
            if "\\x00" in ssid:
                ssid = "Hidden"
            rssis[ssid] = rssi
        if line_len == 4:
            (MAC, freq , rssi, secu) = line.split()
            ssid = "HIDDEN"
        if line_len >=4:
            if "WPA2" in secu:
                secu = "WPA2"
            if "WPS" in secu:
                secu = "WPS"
            if "ESS" in secu:
                secu = "OPEN"
            secus[ssid] = secu

    for s in rssis.keys():
        value=collections.OrderedDict()
        value["ssid"]=s
        value["rssi"]=rssis[s]
        value["secu"]=secus[s]
        values.append(value)

    json_string=json.dumps(values, separators=(',', ':'))

    print(json_string)

    # dmesg_print(json_string)


if __name__=="__main__":
    main()
