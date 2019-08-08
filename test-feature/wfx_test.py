#!/usr/bin/python3
# -*- coding: utf-8 -*-

from wfx_test_functions import *
from wfx_connection import *


def init_board(wlan_name="wf200"):
    """ Called to restart from a fresh copy of the template,
         after reloading the firmware.
        1- reload driver (hence reload FW & PDS data from /lib/firmware)
        2- retrieve current FW version
        3- generate the current pds tree based on the FW version
    """
    pi("wlan pi_traces  on")
    pi("wlan pds_traces on")

    _pds = PdsTree()

    pi(wlan_name + " " + "sudo killall -wq wpa_supplicant hostapd wpa_gui lighttpd")
    pi(wlan_name + " " + "sudo wfx_driver_reload -C")
    time.sleep(0.5)
    wf200_fw = fw_version("refresh")

    _pds.fill_tree(wf200_fw)

    pi("wlan pi_traces on")
    pi("wlan pds_traces off")
    # Recent kernel versions increment the phy index, so let's retrieve it
    pds_env['PHY'] = pi("wlan sudo ls /sys/kernel/debug/ieee80211/")
    pds_env['SEND_PDS_FILE'] = "/sys/kernel/debug/ieee80211/" + pds_env['PHY'] + "/wfx/send_pds"
    pds_definition_file = pi("wlan ls " + pds_env['PDS_DEFINITION_ROOT'] + pds_env['PDS_DEFINITION_FILE'])
    if pds_definition_file == "":
        # Backward compatibility with previous naming scheme...
        definitions_files = pi(wlan_name + " " + "ls " + pds_env['PDS_DEFINITION_ROOT'] + \
             " | grep 'definitions-.*.in'").split("\n")
        definitions_versions = []
        for i in definitions_files:
            definitions_versions.append(i.replace("definitions-","").replace(".in",""))
        definitions_versions.sort(key=StrictVersion)

        for definition in definitions_versions:
            if StrictVersion(definition) <= StrictVersion(wf200_fw):
                    pds_env['PDS_DEFINITION_FILE'] = "definitions-" + definition + ".in"
            else:
                break
        print("Backward compatibility : Using PDS definitions from " + pds_env['PDS_DEFINITION_FILE'])

    with open(pds_env['PDS_DEFINITION_ROOT'] + pds_env['PDS_DEFINITION_FILE'] , 'r') as f:
        if "definitions_legacy" in f.read():
            wfx_pds_tree.pds_compatibility_text = ""

    print("\nDriver reloaded, FW" + wf200_fw + "\n")
    if StrictVersion(_pds.current_fw_version) > StrictVersion(wf200_fw):
        print("PDS tree filled with parameters supported by FW" + wf200_fw + " (not the latest FW)\n")
    elif StrictVersion(_pds.current_fw_version) == StrictVersion(wf200_fw):
        print("PDS tree filled with parameters supported by FW" + _pds.current_fw_version + "\n")
    else:
        print("PDS tree filled with parameters supported by FW" + _pds.current_fw_version + " (FW more recent than wfx_pds_tree)\n")
    print(_pds.pretty())
    return _pds


def init_tree(firmware):
    _pds = PdsTree()
    _pds.fill_tree(firmware)
    print(_pds.pretty())
    return _pds


def init_pi(wlan_name="wf200"):
    """ Called to restart from a fresh copy of the template,
         after reloading the firmware.
        1- reload driver (hence reload FW & PDS data from /lib/firmware)
        2- retrieve current FW version
        3- generate the current pds tree based on the FW version
    """
    pi("wlan pi_traces  on")
    pi("wlan pds_traces on")

    _pds = PdsTree()

    pi(wlan_name + " " + "sudo killall -wq wpa_supplicant hostapd wpa_gui lighttpd")
    pi(wlan_name + " " + "sudo wfx_driver_reload -C")
    time.sleep(0.5)
    wf200_fw = fw_version("refresh")

    _pds.fill_tree(wf200_fw)

    pi("wlan pi_traces on")
    pi("wlan pds_traces off")
    # Recent kernel versions increment the phy index, so let's retrieve it
    pds_env['PHY'] = pi("wlan sudo ls /sys/kernel/debug/ieee80211/")
    pds_env['SEND_PDS_FILE'] = "/sys/kernel/debug/ieee80211/" + pds_env['PHY'] + "/wfx/send_pds"
    pds_definition_file = pi("wlan ls " + pds_env['PDS_DEFINITION_ROOT'] + pds_env['PDS_DEFINITION_FILE'])
    if pds_definition_file == "":
        # Backward compatibility with previous naming scheme...
        definitions_files = pi(wlan_name + " " + "ls " + pds_env['PDS_DEFINITION_ROOT'] + \
             " | grep 'definitions-.*.in'").split("\n")
        definitions_versions = []
        for i in definitions_files:
            definitions_versions.append(i.replace("definitions-","").replace(".in",""))
        definitions_versions.sort(key=StrictVersion)

        for definition in definitions_versions:
            if StrictVersion(definition) <= StrictVersion(wf200_fw):
                    pds_env['PDS_DEFINITION_FILE'] = "definitions-" + definition + ".in"
            else:
                break
        print("Backward compatibility : Using PDS definitions from " + pds_env['PDS_DEFINITION_FILE'])

    with open(pds_env['PDS_DEFINITION_ROOT'] + pds_env['PDS_DEFINITION_FILE'] , 'r') as f:
        if "definitions_legacy" in f.read():
            wfx_pds_tree.pds_compatibility_text = ""

    print("\nDriver reloaded, FW" + wf200_fw + "\n")
    if StrictVersion(_pds.current_fw_version) > StrictVersion(wf200_fw):
        print("PDS tree filled with parameters supported by FW" + wf200_fw + " (not the latest FW)\n")
    elif StrictVersion(_pds.current_fw_version) == StrictVersion(wf200_fw):
        print("PDS tree filled with parameters supported by FW" + _pds.current_fw_version + "\n")
    else:
        print("PDS tree filled with parameters supported by FW" + _pds.current_fw_version + " (FW more recent than wfx_pds_tree)\n")
    print(_pds.pretty())
    return _pds


if __name__ == '__main__':
    pds = init_board()

    print(channel())
    print(tone())
    print(tone_power())
    print(tx_power())
    print(tx_backoff())
    print(tx_framing())
    print(tx_mode())
    print(tx_rx_select())

    print(channel(7))
    print(channel())

    print(tx_power(11.25))
    print(tx_power())

    print(tx_rx_select(2, 2))
    print(tx_rx_select())

    print(tx_framing())
    print(tx_framing(1, 12))

    print(tx_mode())
    print(tx_backoff())

    print(tx_stop())
    print(pds.pretty())

    print(wfx_get_list({'TEST_MODE','NB_FRAME'}))

    print(wfx_set_dict({'NB_FRAME':25},0))
    print(wfx_get_list({'NB_FRAME'}))

    # Sending data with temporary items named with single lowercase path and names will work (up to PDS data sending), provided that the FW supports the path and names!
    # print(PdsTree.add_tmp_param(pds, '2.0', 'z.a.a', 'x', '12'))
    # print(PdsTree.add_tmp_param(pds, '2.0', 'z.a.b', 'y', '25'))
    # print(wfx_set_dict({'x':15, 'y':32},1))

    # Sending data with temporary items named with 'human-readable' names will only work if the path items and names are declared in definitions.in!
    print(PdsTree.add_tmp_param(pds, '2.0', 'HEADER', 'VERSION_MAJOR', '2'))
    print(PdsTree.add_tmp_param(pds, '2.0', 'HEADER', 'VERSION_MINOR', '2'))
    print(wfx_get_list({'VERSION_MAJOR','VERSION_MINOR' }))

    print(pds.pretty())

