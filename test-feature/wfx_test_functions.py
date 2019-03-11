#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""wfx_test_functions.py

    These functions adapt the test API to the underlying FW API

"""

import os
import re
from wfx_test_core import *

print("wfx_test_functions running from " + os.path.dirname(os.path.abspath(__file__)))


def channel(ch=None):
    if ch is None:
        return wfx_get_list({'TEST_CHANNEL_FREQ'})
    else:
        return wfx_set_dict({'TEST_CHANNEL_FREQ': ch})


def tone(cmd=None, freq=0):
    # CW Mode: generate CW @ (freq+1)*312.5Khz
    if cmd is None:
        test_mode = wfx_get_list({"TEST_MODE"}, mode='quiet')
        if test_mode == "tx_cw":
            return wfx_get_list({"TEST_MODE"})
        else:
            return wfx_get_list({"TEST_MODE", "NB_FRAME"})
    else:
        if cmd == "start":
            return wfx_set_dict({"TEST_MODE": "tx_cw", "CW_MODE": "single", "FREQ1": freq})
        elif cmd == "stop":
            return wfx_set_dict({"TEST_MODE": "tx_packet", "NB_FRAME": 100})


def tone_power(dbm=None):
    if dbm is None:
        power = int(wfx_get_list({"MAX_OUTPUT_POWER"}, mode='quiet'))
        return "MAX_OUTPUT_POWER  " + str(power) + "  " + "     tone_power  " + str(power/4.0) + " dBm"
    else:
        return wfx_set_dict({"MAX_OUTPUT_POWER": int(4*dbm)})


def tx_power(dbm=None):
    if dbm is None:
        power = int(wfx_get_list("MAX_OUTPUT_POWER_QDBM", mode='quiet'))
        return "MAX_OUTPUT_POWER_QDBM" + "  " + str(power) + \
            "     tx_power  " + str(power/4.0) + " dBm"
    else:
        return wfx_set_dict({"MAX_OUTPUT_POWER_QDBM": int(4*dbm)})


def tx_backoff(mode_802_11=None, backoff_level=0):
    if backoff_level == "":
        backoff_level = 0
    if mode_802_11 == "RSVD":
        return
    if mode_802_11 is None:
        backoff_val = wfx_get_list({"BACKOFF_VAL"}, mode='quiet')
        (backoff_data, nb) = re.subn('\[|\]| ', '', backoff_val)
        backoff_max = max(backoff_data.split(','))
        backoff_dbm = str(int(backoff_max)/4.0)
        return "BACKOFF_VAL  " + backoff_max + "     tx_backoff  " + backoff_dbm + " dB"
    else:
        if "DSSS" in mode_802_11:
            index = 0
        elif "6Mbps" in mode_802_11 or "MCS0" in mode_802_11:
            index = 1
        elif "9Mbps" in mode_802_11:
            index = 1
        elif "12Mbps" in mode_802_11 or "MCS1" in mode_802_11:
            index = 1
        elif "18Mbps" in mode_802_11 or "MCS2" in mode_802_11:
            index = 2
        elif "24Mbps" in mode_802_11 or "MCS3" in mode_802_11:
            index = 2
        elif "36Mbps" in mode_802_11 or "MCS4" in mode_802_11:
            index = 3
        elif "48Mbps" in mode_802_11 or "MCS5" in mode_802_11:
            index = 3
        elif "54Mbps" in mode_802_11 or "MCS6" in mode_802_11:
            index = 4
        elif "MCS7" in mode_802_11:
            index = 5
        else:
            return "Unknown 802.11 mode"    
        value = [0, 0, 0, 0, 0, 0]
        value[index] = int(4 * backoff_level)
        wfx_set_dict({"BACKOFF_VAL": str(value)})


def tx_framing(packet_length_bytes=None, delay_between_us=100):
    if packet_length_bytes is None:
        return wfx_get_list({"FRAME_SIZE_BYTE", "IFS_US"})
    else:
        return wfx_set_dict({"FRAME_SIZE_BYTE": packet_length_bytes, "IFS_US": delay_between_us})


def tx_mode(mode_802_11=None):
    if mode_802_11 is None:
        return wfx_get_list({"HT_PARAM", "RATE"})
    else:
        res = re.findall("([^_]*)_(.*)", mode_802_11)
        suffix = res[0][1]
        ht_param = "MM"
        if "GF_" in mode_802_11:
            rate = "N_" + suffix
            ht_param = "GF"
        elif "MM_" in mode_802_11:
            rate = "N_" + suffix
        elif "LEG_" in mode_802_11:
            rate = "G_" + suffix
        elif "DSSS_" in mode_802_11:
            rate = "B_" + suffix + "Mbps"
        elif "CCK_" in mode_802_11:
            rate = "B_" + suffix + "Mbps"
        else:
            return "Unknown 802.11 mode"
        return wfx_set_dict({"HT_PARAM": ht_param, "RATE": rate})


def tx_rx_select(tx_ant=None, rx_ant=None):
    if tx_ant is None:
        return wfx_get_list({"RF_PORTS"})
    else:
        return wfx_set_dict({"RF_PORTS": "TX" + str(tx_ant) + "_RX" + str(rx_ant)})


def tx_start(nb_frames=None):
    if nb_frames is None:
        return wfx_get_list({"TEST_MODE", "NB_FRAME"})
    else:
        if str(nb_frames) == "continuous":
            nb_frames = 0
        return wfx_set_dict({"TEST_MODE": "tx_packet", "NB_FRAME": nb_frames})


def tx_stop():
    return wfx_set_dict({"NB_FRAME": 100})


if __name__ == '__main__':
    print("\n# pds = PdsTree(pds_structure)")
    pds = PdsTree()
    print("\n# pds.fill_tree(\"2.0\")")
    pds.fill_tree("2.0")

    print("\n# pds.pretty():")
    print(pds.pretty())

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
