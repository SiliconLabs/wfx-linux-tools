#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""wfx_test_core.py
# This module first sets the python environment variables
# The functions in this module provide generic access to
#    * the PDS file
#    * system calls
#
#        Setting a single parameter: (PDS section sent immediately)
#        wfx_set_dict({'NB_FRAME': 22})
#
#        Setting several parameters: (PDS section(s) sent once all set)
#        wfx_set_dict({'NB_FRAME': 32, 'RF_PORTS': 'x1'})
#
#        Checking a single parameter:
#        wfx_get_list({'RF_PORTS'})
#
#        Checking several parameters
#        wfx_get_list({'NB_FRAME', 'RF_PORTS'})
"""

import subprocess
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--internal', action='store_true', help='(flag) uses internal test path')

args = parser.parse_args()

pds_env = dict()

pds_env['PDS_CURRENT_FILE'] = "/tmp/current_pds_data.in"
pds_env['PHY'] = "phy0"
pds_env['SEND_PDS_FILE'] = "/sys/kernel/debug/ieee80211/" + pds_env['PHY'] + "/wfx/send_pds"
pds_env['PDS_DEFINITION_FILE'] = "definitions.in"

from wfx_pds_tree import *
import wfx_pds_tree

pi_traces = 1
pds_traces = 1

fw_label = ""
pds_warning = ""


def fw_version(refresh=None):
    """ Retrieving the FW version from dmesg """
    global fw_label
    if refresh is not None:
        res = pi("wf200 sudo wfx_show | grep 'Firmware loaded version:'")
        if len(res) == 0:
            print("Error: Can not determine FW_version. Assuming max (FW" + wfx_pds_tree.trunk.max_fw_version + ")")
            return wfx_pds_tree.trunk.max_fw_version
        else:
            fw_label = res.split(':')[1].strip()
    return fw_label


def send(_pds, parameters, send_data=1):
    """ Sending compressed PDS file content to FW """
    global pds_traces
    res = ""
    _sub = PdsTree.sub_tree(_pds, parameters)

    pds_sections = _sub.pretty()

    pds_string = "#include \"" + pds_env['PDS_DEFINITION_ROOT'] + pds_env['PDS_DEFINITION_FILE'] + "\"\n\n" + wfx_pds_tree.pds_compatibility_text + pds_sections

    pds_current_file = open(pds_env['PDS_CURRENT_FILE'], 'w')
    pds_current_file.write(pds_string)
    pds_current_file.close()

    compressed_string = pi("wf200 pds_compress " + pds_env['PDS_CURRENT_FILE'] + " 2>&1")

    if ":error:" in compressed_string:
        res += "WARNING: No pds data sent! " + compressed_string + "\n"
        add_pds_warning("WARNING: No pds data sent! " + compressed_string + "\n")
    else:
        if pds_traces:
            print("      " + compressed_string)
        if send_data == 1:
            res += pi("wf200 sudo pds_compress " + pds_env['PDS_CURRENT_FILE'] + " " +
                      pds_env['SEND_PDS_FILE'] + " 2>&1") + "\n"
        else:
            res += " not sent, waiting for tone('start'), tx_start(..) or rx_start()"
            add_pds_warning(" not sent, waiting for tone('start'), tx_start(..) or rx_start()\n")
    return res.strip()


def wfx_set_dict(param_dict, send_data=1):
    res = ''
    parameters = []
    for p, v in param_dict.items():
        parameter = str(p)
        value = str(v)
        res += parameter + '  '
        res += str(PdsTree.set(wfx_pds_tree.trunk, parameter, value)) + '     '
        parameters.append(parameter)
    res += str(send(wfx_pds_tree.trunk, parameters, send_data))
    return res.strip()


def wfx_get_list(param_list, mode='verbose'):
    res = ''
    if type(param_list) is str:
        my_list = []
        for item in param_list.split(","):
            my_list.append(str(item).strip())
        param_list = my_list
    if type(param_list) is set:
        my_list = []
        for list_item in param_list:
            for item in list_item.split(","):
                my_list.append(str(item).strip())
        param_list = my_list
    for parameter in param_list:
        if mode == 'verbose':
            res += parameter + '  '
        res += PdsTree.get(wfx_pds_tree.trunk, parameter) + '     '
    return res.strip()


def pi(_args):
    """ Providing access to system or wf200 functions """
    global pi_traces
    global pds_traces

    split_args = _args.split()
    if len(split_args) == 0:
        return "wfx_test_core.pi: no arguments?"
    target = split_args[0]
    if len(split_args) <= 1:
        return "wfx_test_core.pi: no arguments for target " + target + "?"
    cmd = split_args.copy()
    del cmd[0]
    cmd_args = cmd.copy()
    del cmd_args[0]
    if target in "Hello":
        return "Hi!"
    if target in "wf200 wlan":
        if cmd[0] in ["help"]:
            return "Available " + target + \
                   " commands:\n      pi_traces  <on/off>\n      pds_traces <on/off>\n" + \
                   "      kernel\n" + \
                   "     <unknown commands are processed by system>\n"                 
        elif cmd[0] in ["pi_traces"]:
            if len(cmd) > 1:
                if cmd[1] == "on":
                    pi_traces = 1
                if cmd[1] == "off":
                    pi_traces = 0
            return "wfx_test_core.pi: pi_traces " + str(pi_traces)
        elif cmd[0] in ["pds_traces"]:
            if len(cmd) > 1:
                if cmd[1] == "on":
                    pds_traces = 1
                if cmd[1] == "off":
                    pds_traces = 0
            return "wfx_test_core.pi: pds_traces " + str(pds_traces)
        elif cmd[0] in ["kernel"]:
            return pi(target + " " + "uname -a")
        else:
            if pi_traces:
                print("wfx_test_core.pi: Execute:  " + ' '.join(cmd))
            op = subprocess.Popen(' '.join(cmd), shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if op:
                output = str(op.stdout.read(), "utf-8").strip()
                if pi_traces:
                    for line in output.split("\n"):
                        print("wfx_test_core.pi:  > > > :  " + line)
                return output
            else:
                error = str(op.stderr.read(), "utf-8").strip()
                print("wfx_test_core.pi: Error:", error)
                return error
    else:
        return "wfx_test_core.pi: Target '" + target + "' not supported\n"


def internal(yes_no=True):
    if yes_no:
        print("internal mode")
        pds_env['PDS_DEFINITION_ROOT'] = "/home/pi/siliconlabs/wfx_pds/definitions/"
    else:
        print("customer mode")
        pds_env['PDS_DEFINITION_ROOT'] = "/home/pi/siliconlabs/wfx-firmware/PDS/"


if args.internal:
    internal(True)
else:
    internal(False)


if __name__ == '__main__':
    del sys.argv[0]
    print(pi(' '.join(sys.argv)))

    pds = PdsTree()
    print("\n# pds.fill_tree(\"2.0\")")
    pds.fill_tree("2.0")
    print(pds.pretty())

    print("wfx_set_dict({'NB_FRAME': 22})")
    print(wfx_set_dict({'NB_FRAME': 22}))

    print("wfx_set_dict({'NB_FRAME': 32, 'RF_PORTS': 'TX1_RX1'}")
    wfx_set_dict({'NB_FRAME': 32, 'RF_PORTS': 'TX1_RX1'})

    print("wfx_set_dict({'RF_PORT': 'RF_PORT_1'}")
    wfx_set_dict({'RF_PORT': 'RF_PORT_1'})

    print("wfx_get_list({'RF_PORT'})")
    print('RF_PORT = ' + wfx_get_list({'RF_PORT'}))
    
    print("wfx_get_list({'NB_FRAME', 'RF_PORTS'})")
    print('NB_FRAME & RF_PORTS = ' + wfx_get_list({'NB_FRAME', 'RF_PORTS'}))
    print("wfx_get_list('TEST_CHANNEL_FREQ' " + wfx_get_list('TEST_CHANNEL_FREQ'))

    print("wfx_set_dict({'RF_PORT': 'RF_PORT_1'}")
    wfx_set_dict({'RF_PORT': 'RF_PORT_1'})

    print("wfx_get_list({'RF_PORT'})")
    print('RF_PORT = ' + wfx_get_list({'RF_PORT'}))
