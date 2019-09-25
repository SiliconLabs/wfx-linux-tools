#!/usr/bin/python
from cgi_commons import *

import sys
import json
import collections

missing_fields = []

if "ssid" not in form:
    missing_fields.append("ssid")
else:
    ssid = form.getfirst("ssid","")

if "secu" not in form:
    missing_fields.append("secu")
else:
    secu = form.getfirst("secu","")
    if secu != "OPEN":
        if "pwd" not in form:
            missing_fields.append("pwd")
        else:
            pwd = form.getfirst("pwd","")

    if len(missing_fields) == 0:
        bash_res("wpa_cli flush", trace)
        network_id = bash_res("wpa_cli add_network", trace).split()[3]
        bash_res('wpa_cli set_network    ' + network_id + ' ssid \\"' + ssid + '\\"', trace)

        if secu == "WPA2":
            bash_res('wpa_cli set_network    ' + network_id + ' key_mgmt ' + 'WPA-PSK' + '', trace)
            bash_res('wpa_cli set_network    ' + network_id + ' psk \\"' + pwd + '\\"', trace)
        else:
            bash_res('wpa_cli set_network    ' + network_id + ' key_mgmt ' + 'NONE' + '', trace)
            bash_res('wpa_cli set_network    ' + network_id + ' proto ' + 'RSN' + '', trace)

        bash_res('wpa_cli select_network    ' + network_id, trace)
        # we have to print at least something, so let's print the network_id
        print(network_id)

if len(missing_fields):
    print('missing_fields: ' + str(missing_fields))
