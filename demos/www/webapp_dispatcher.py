#!/usr/bin/python3
# We need to call bash scripts to execute command with superuser
#   privileges when called from a web page
# This works as long as all scripts are chmod'ed with a+rx

# Several functions in this module can be tested from command line using:
#  python3 webapp_dispatcher.py disconnect_client.cgi?mac=<00:11:22:33:44:55>
#  python3 webapp_dispatcher.py get_interface_states
#  python3 webapp_dispatcher.py get_led_states
#  python3 webapp_dispatcher.py start_scan.cgi
#  python3 webapp_dispatcher.py start_softap.cgi
#  python3 webapp_dispatcher.py start_station.cgi?ssid=<ssid>&pwd=<pwd>&secu=<None/WPA2>
#  python3 webapp_dispatcher.py stop_softap.cgi
#  python3 webapp_dispatcher.py stop_station.cgi
#  python3 webapp_dispatcher.py toggle_led?led_id=0/1
#
#  when used in the Web Application they are called via the webapp.fcgi,
#   which calls the dispatch() function below
#
# Restarting the webapp following changes:
#  sudo systemctl restart wfx-demo-combo.service
#

import collections
import json
import os
import re
import subprocess
import sys
import time

profiling=list()
start_time = time.process_time()
prev_time = start_time

def dispatch(environ):
    dmesg_print("dispatch "+ environ["REQUEST_URI"] + " " + environ["QUERY_STRING"])
    try:
        request_uri = environ["REQUEST_URI"]
        query_string = environ["QUERY_STRING"]

        if "/disconnect_client.cgi" in request_uri:
            return disconnect_client(query_string)

        if "/get_interface_states.cgi" in request_uri:
            return get_interface_states()

        if "/get_led_states.cgi" in request_uri:
            return get_led_states()

        if "/start_scan.cgi" in request_uri:
            return start_scan()

        if "/start_station.cgi" in request_uri:
            return start_station(query_string)

        if "/start_softap.cgi" in request_uri:
            return start_softap()

        if "/stop_station.cgi" in request_uri:
            return stop_station()

        if "/stop_softap.cgi" in request_uri:
            return stop_softap()

        if "/toggle_led.cgi" in request_uri:
            return toggle_led(query_string)
              
        return "Can't dispatch " + request_uri

    except Exception as e:
        return str(e)

def bash_res(cmd, trace=0):
    trace_cmd = 0
    trace_res = 0
    if str(trace).isdigit():
        trace = int(str(trace))
        if trace > 1:
            trace_cmd = (trace >> 1) & 0x1
            trace_res = (trace >> 2) & 0x1
        else:
            trace_cmd = trace
            trace_res = trace
    else:
        trace = 0
    if trace_cmd:
        print("<>cmd<>" + cmd + "<>cmd<>")
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    ret = res.stdout.read().strip()
    if trace_res:
        print("<>res<>" + ret.decode() + "<>res<>")
    return ret.decode()

def start_station(query_string, trace=1):
    bash_res("sudo /bin/systemctl start wfx-demo-wpa_supplicant.service")
    missing_fields = []

    if "ssid=" not in query_string:
        missing_fields.append("ssid")
    else:
        ssid = re.findall(r'ssid=([^&]*)', query_string)[0]

    if "secu" not in query_string:
        missing_fields.append("secu")
    else:
        secu = re.findall(r'secu=([^&]*)*', query_string)[0]
        if secu != "OPEN":
            if "pwd" not in query_string:
                missing_fields.append("pwd")
            else:
                pwd = re.findall(r'pwd=([^&]*)*', query_string)[0]

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
            # we have to return something, so let's return the ssid
            return(ssid)

    if len(missing_fields):
        return('missing_fields: ' + str(missing_fields))

def start_softap():
    return bash_res("sudo /bin/systemctl start wfx-demo-hostapd.service")

def stop_station():
    return bash_res("sudo /bin/systemctl stop wfx-demo-wpa_supplicant.service")

def stop_softap():
    return bash_res("sudo /bin/systemctl stop wfx-demo-hostapd.service")

def disconnect_client(query_string):
    if "mac=" in query_string:
        macs = re.findall(r'mac=([a-fA-F0-9]{2}:[a-fA-F0-9]{2}:[a-fA-F0-9]{2}:[a-fA-F0-9]{2}:[a-fA-F0-9]{2}:[a-fA-F0-9]{2})', query_string)
        if macs != []:
            hostapd_cli_all_sta = bash_res("hostapd_cli all_sta")
            mac_all_sta = re.findall(r'dot11RSNAStatsSTAAddress.*=(.*)', hostapd_cli_all_sta)
            mac = macs[0]
            if mac in mac_all_sta:
                return str(bash_res("hostapd_cli disassociate " + mac))
            else:
                return ("mac address '" + mac + "' is not currently associated")
        else:
            return ("Incorrect mac address in '" + query_string + "': A proper mac has the form 'mac=00:11:22:33:44:55'")
    else:
        return ("Argument error: A proper request is 'disconnect_client.cgi?mac=00:11:22:33:44:55'")

def dmesg_print(txt):
    bash_res("echo " + txt + " > /dev/kmsg")

def get_interface_states():
    # We use collections.OrderedDict() instead of dict() because
    #  the web page refers to the json content as info[n].state,
    # As a consequence, the order of the following lines is FIXED

    states = collections.OrderedDict()

    softap = collections.OrderedDict()

    misc = collections.OrderedDict()

    hostapd_running = bash_res("ps -few | grep hostapd | grep ^root")
    if hostapd_running == "":
        softap_conf = bash_res("cat /home/pi/siliconlabs/wfx-linux-tools/demos/conf/combo_hostapd.conf")
        show_wlan1 = bash_res("ip address show wlan1")
        softap["state"] = "0"
        softap["ssid"] = re.findall(r'\nssid.*=(.*)', softap_conf)[0]
        softap["ip"] = re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', show_wlan1)[0]
        softap["mac"] = re.findall(r'[0-9|a-f]{2}\:[0-9|a-f]{2}\:[0-9|a-f]{2}\:[0-9|a-f]{2}\:[0-9|a-f]{2}\:[0-9|a-f]{2}', show_wlan1)[0]
        softap["secu"] = "(AP is off)"
        softap["channel"] = re.findall(r'\nchannel=(.*)', softap_conf)[0]
        softap["clients"] = list()
    else:
        softap["state"] = "1"
        hostapd_cli_status = bash_res("hostapd_cli status")
        hostapd_cli_config = bash_res("hostapd_cli get_config")
        softap["ssid"] = re.findall(r'\nssid.*=(.*)', hostapd_cli_config)[0]
        softap["ip"] = bash_res("ip address show wlan1 | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}'")
        softap["mac"] = re.findall(r'bssid.*=(.*)', hostapd_cli_config)[0]
        softap["secu"] = re.findall(r'key_mgmt.*=(.*)', hostapd_cli_config)[0]
        softap["channel"] = re.findall(r'\nchannel.*=(.*)', hostapd_cli_status)[0]
        num_sta = int(re.findall(r'\nnum_sta\[.*\]=(.*)', hostapd_cli_status)[0])
        softap["clients"] = list()
        if num_sta > 0:
            hostapd_cli_all_sta = bash_res("hostapd_cli all_sta")
            dnsmasq_leases = bash_res("cat /var/lib/misc/dnsmasq.leases")
            mac_all_sta = re.findall(r'dot11RSNAStatsSTAAddress.*=(.*)', hostapd_cli_all_sta)
            for mac in mac_all_sta:
                client = collections.OrderedDict()
                if mac in dnsmasq_leases:
                    ip, hostname = re.findall(r' ' + mac + r' ' + r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})' + r' ' + r'(\S*)' , dnsmasq_leases)[0]
                    client["ip"] = ip
                    client["mac"] = mac
                    client["hostname"] = hostname
                    softap["clients"].append(client)

        
    wpa_supplicant_running = bash_res("ps -few | grep wpa_supplicant-combo | grep ^root ")
    station = collections.OrderedDict()

    station["state"] = "0"
    station["ip"] = "0.0.0.0"
    station["mac"] = "00:00:00:00:00:00"
    ap = collections.OrderedDict()
    ap["ssid"] = ""
    ap["mac"] = "00:00:00:00:00:00"
    ap["secu"] = ""
    ap["channel"] = 0
    if wpa_supplicant_running != "":
        wpa_cli_status = bash_res("wpa_cli status")
        #misc["wpa_cli_status"] = wpa_cli_status
        station["state"] = re.findall(r'\nwpa_state.*=(.*)', wpa_cli_status)[0]
        if station["state"] == "COMPLETED":
            station["ip"] = re.findall(r'\nip_address=(.*)', wpa_cli_status)[0]
            station["mac"] = re.findall(r'\nbssid=(.*)', wpa_cli_status)[0]
            station["state"] = 1
            ap["ssid"] = re.findall(r'\nssid=(.*)', wpa_cli_status)[0]
            ap["mac"] = re.findall(r'\naddress=(.*)', wpa_cli_status)[0]
            ap["secu"] = re.findall(r'\nkey_mgmt=(.*)', wpa_cli_status)[0]
            freq = int(re.findall(r'\nfreq=(.*)', wpa_cli_status)[0])
            ap["channel"] = str(int((freq - 2407)/5))

    station["ap"] = ap

    misc["whoami"] = bash_res("whoami")

    states["softap"] = softap
    states["station"] = station
    states["misc"] = misc

    json_string = json.dumps(states, separators=(',', ':'))
    return(json_string)

def get_led_states():
    state=collections.OrderedDict()
    state["LED0"] = read_led_state(0)
    state["LED1"] = read_led_state(1)

    values=list()
    for s in state.keys():
        value=collections.OrderedDict()
        value["name"]=s
        value["state"]=state[s]
        values.append(value)

    json_string=json.dumps(values, separators=(',', ':'))
    return json_string

def profile(txt="", from_start=None):
    global start_time
    global prev_time
    p = collections.OrderedDict()
    if from_start is None:
        p[txt] = str.format("%d" % ((time.clock() - prev_time)*1000))
    else:
        p[txt] = str.format("%d" % ((time.clock() - start_time)*1000))
    prev_time = time.clock()
    profiling.append(p)

def read_led_state(led_id):
    f = open(f'/sys/class/leds/led{led_id}/trigger')
    if '[none]' in f.read():
        return 0
    else:
        return 1

def start_scan():
    scan_result = bash_res("./start_scan.sh")

    aps = list()
    for line in scan_result.split("\n"):
        line_len = len(line.split())
        ssid = "?"
        secu = "?"
        if line_len == 5:
            (MAC, freq , rssi, secu, ssid) = line.split()
            if "\\x00" in ssid:
                ssid = "HIDDEN"
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

        channel = str(int((int(freq) - 2407)/5))
        aps.append((MAC, freq, channel, rssi, secu, ssid))

    aps.sort(key = lambda elt : elt[3], reverse = False)

    values = list()
    for MAC, freq, channel, rssi, secu, ssid in aps:
        value=collections.OrderedDict()
        value["ssid"] = ssid
        value["secu"] = secu
        value["rssi"] = rssi
        value["channel"] = channel
        values.append(value)

    json_string=json.dumps(values, separators=(',', ':'))

    return (json_string)

def toggle_led(led):
    if "led_id=" in led:
        led_id = re.findall(r'led_id=(.*)', led)[0]
        # Check that led_id is a digit as a measure of protection against hackers
        if led_id.isdigit():
            f = open(f'/sys/class/leds/led{led_id}/trigger')
            led_trigger = f.read()
            if '[none]' in led_trigger:
                bash_res("echo default-on > /sys/class/leds/led" + led_id + "/trigger")
                return "1"
            else:
                bash_res("echo none       > /sys/class/leds/led" + led_id + "/trigger")
                bash_res("echo 0          > /sys/class/leds/led" + led_id + "/brightness")
                return "0"
        else:
            return ("Argument error: led_id is not a digit. A proper request is 'led_toggle.cgi?led_id=0/1'")
    else:
        return ("Argument error: A proper request is 'led_toggle.cgi?led_id=0/1'")

dmesg_print("webapp_dispatcher loaded")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(get_led_states())
        toggle_led('0')
        toggle_led('1')
        print(get_led_states())
    else:
        environ = collections.OrderedDict()
        if "?" in sys.argv[1]:
            environ["REQUEST_URI"], environ["QUERY_STRING"] = ("/" + sys.argv[1]).split("?")
        else:
            environ["REQUEST_URI"] = "/" + sys.argv[1]
            environ["QUERY_STRING"] = ""
        print(dispatch(environ))
    