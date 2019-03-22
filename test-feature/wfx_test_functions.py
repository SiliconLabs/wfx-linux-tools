#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""wfx_test_functions.py

    These functions adapt the test API to the underlying PDS API

    NB: Functions dealing with TEST_FEATURE_CFG parameters don't send 
      PDS data immediately. TEST_FEATURE_CFG PDS data is sent when calling start()

"""

import os
import re
from wfx_test_core import *

print("wfx_test_functions running from " + os.path.dirname(os.path.abspath(__file__)))


def channel(ch=None):
    if ch is None:
        return wfx_get_list({'TEST_CHANNEL_FREQ'})
    else:
        return wfx_set_dict({'TEST_CHANNEL_FREQ': ch}, send_data=0)


def dmesg_period(period=None):
    if period is None:
        return wfx_get_list({'TEST_IND'})
    else:
        return wfx_set_dict({'TEST_IND': period}, send_data=0)


def tone(cmd=None, freq=None):
    if freq is None:
        freq = wfx_get_list({"FREQ1"}, mode = 'quiet')
    # CW Mode: generate CW @ (freq+1)*312.5Khz
    if cmd is None:
        test_mode = wfx_get_list({"TEST_MODE"}, mode='quiet')
        if test_mode == "tx_cw":
            return wfx_get_list({"TEST_MODE"})
        else:
            return wfx_get_list({"TEST_MODE", "NB_FRAME"})
    else:
        if cmd == "start":
            return wfx_set_dict({"TEST_MODE": "tx_cw", "CW_MODE": "single", "FREQ1": freq}, send_data=1)
        elif cmd == "stop":
            return tx_stop()


def tone_power(dbm=None):
    if dbm is None:
        power = int(wfx_get_list({"MAX_OUTPUT_POWER"}, mode='quiet'))
        return "MAX_OUTPUT_POWER  " + str(power) + "  " + "     tone_power  " + str(power/4.0) + " dBm"
    else:
        return wfx_set_dict({"MAX_OUTPUT_POWER": int(4*dbm)}, send_data=0)


def tx_power(dbm=None):
    if dbm is None:
        power = int(wfx_get_list("MAX_OUTPUT_POWER_QDBM", mode='quiet'))
        return "MAX_OUTPUT_POWER_QDBM" + "  " + str(power) + \
            "     tx_power  " + str(power/4.0) + " dBm"
    else:
        return wfx_set_dict({"MAX_OUTPUT_POWER_QDBM": int(4*dbm), "TEST_MODE": "tx_packet", "NB_FRAME": 0}, send_data=1)


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
        backoff_indexes_by_bitrate = {
            0: ['1Mbps' , '2Mbps', '5_5Mbps' , '11Mbps'],
            1: ['6Mbps' , '9Mbps', '12Mbps'],
            2: ['18Mbps', '24Mbps'],
            3: ['36Mbps', '48Mbps'],
            4: ['54Mbps']
        }
        backoff_indexes_by_modulation = {
            0: ['DSSS', 'CCK'],
            1: ['MCS0', 'MCS1'],
            2: ['MCS2', 'MCS3'],
            3: ['MCS4', 'MCS5'],
            4: ['MCS6'],
            5: ['MCS7']
        }
        index = -1
        if 'Mbps' in mode_802_11:
            input_bitrate = '_'.join(mode_802_11.split('_')[1:])
            for i in backoff_indexes_by_bitrate.keys():
                for bitrate in backoff_indexes_by_bitrate[i]:
                    if bitrate == input_bitrate:
                        index = i
        else:
            for i in backoff_indexes_by_modulation.keys():
                modulations = backoff_indexes_by_modulation[i]
                for modulation in modulations:
                    if modulation in mode_802_11:
                        index = i
        if index == -1:
            warning_msg = "tx_backoff: Unknown 802.11 mode " + str(mode_802_11)
            add_pds_warning(warning_msg)
            return warning_msg
        value = [0, 0, 0, 0, 0, 0]
        value[index] = int(4 * backoff_level)
        wfx_set_dict({"BACKOFF_VAL": str(value), "TEST_MODE": "tx_packet", "NB_FRAME": 0}, send_data=1)


def tx_framing(packet_length_bytes=None, delay_between_us=100):
    if packet_length_bytes is None:
        return wfx_get_list({"FRAME_SIZE_BYTE", "IFS_US"})
    else:
        return wfx_set_dict({"FRAME_SIZE_BYTE": packet_length_bytes, "IFS_US": delay_between_us}, send_data=0)


def tx_mode(mode_802_11=None):
    if mode_802_11 is None:
        return wfx_get_list({"HT_PARAM", "RATE"})
    else:
        res = re.findall("([^_]*)_(.*)", mode_802_11)
        mode = res[0][0]
        suffix = res[0][1].replace('Mbps','')
        ht_param = ""
        rate = ""
        ht_param_modes = {
            'MM': ['B', 'DSSS', 'CCK', 'G', 'LEG', 'MM'],
            'GF': ['GF'],
        }
        rate_prefix_modes = {
            'B': ['B', 'DSSS', 'CCK'],
            'G': ['G', 'LEG'],
            'N': ['MM', 'GF'],
        }
        for i in ht_param_modes.keys():
            for param_mode in ht_param_modes[i]:
                if param_mode == mode:
                    ht_param = i
        for i in rate_prefix_modes.keys():
            for rate_prefix in rate_prefix_modes[i]:
                if rate_prefix == mode:
                    rate = i + '_' + suffix
        if 'MCS' not in rate:
            rate += 'Mbps'
        if ht_param == "":
            warning_msg = "tx_mode: Unknown 802.11 mode " + str(mode_802_11)
            add_pds_warning(warning_msg)
            return warning_msg
        return wfx_set_dict({"HT_PARAM": ht_param, "RATE": rate}, send_data=0)


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
        return wfx_set_dict({"TEST_MODE": "tx_packet", "NB_FRAME": nb_frames}, send_data=1)


def tx_stop():
    res = wfx_set_dict({"TEST_MODE": "tx_packet", "NB_FRAME": 100}, send_data=1)
    return res


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

    pi("wf200 pi_traces off")
    pi("wf200 pds_traces on")
    print(tx_rx_select(2, 2))
    print(tx_rx_select())

    print(tx_framing())
    print(tx_framing(1, 12))
    
