#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""wfx_test_functions.py

    These functions adapt the test API to the underlying PDS API

    NB: Functions dealing with TEST_FEATURE_CFG parameters don't send 
      PDS data immediately. TEST_FEATURE_CFG PDS data is sent when calling start()

"""

import os
import re
import time
from wfx_test_core import *
from job import *

print("wfx_test_functions running from " + os.path.dirname(os.path.abspath(__file__)))

global rx_res
global rx_avg
global rx_cnt


def channel(ch=None):
    if ch is None:
        return wfx_get_list({'TEST_CHANNEL_FREQ'})
    else:
        return wfx_set_dict({'TEST_CHANNEL_FREQ': ch}, send_data=0)


def __errors_from_per(nb, per):
    return int((int(nb)*int(per)/10000) + 0.5)


def __per(nb=0, err=0):
    if nb == 0:
        return str.format("%.3e" % (1))
    else:
        return str.format("%.3e" % (int(err) / int(nb)))


def __average(num, count):
    div = 1 if count == 0 else count
    offset = 0.5 if num >=0 else -0.5
    return int((num + offset)/div)


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


def regulatory_mode(reg_mode):
    if reg_mode is None:
        return wfx_get_list("REG_MODE", mode='quiet')
    else:
        possible_reg_modes = ["All", "FCC", "ETSI", "JAPAN", "Unrestricted"]
        old_namings = {"JP":"JAPAN", "min":"All"}
        for n in old_namings.keys():
            if n in reg_mode:
                reg_mode = old_namings[n]
        for m in possible_reg_modes:
            if m in reg_mode:
                return wfx_set_dict({"REG_MODE": "CERTIFIED_" + m}, send_data=0)
        return "Unknown '" + reg_mode + " ' regulatory_mode. Use " + str(possible_reg_modes[0:5])


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


def rx_start():
    res = wfx_set_dict({"TEST_MODE": "rx"}, send_data=1)
    return res


def rx_stop():
    if rx_job is not None:
            rx_job.stop()
    return tx_stop()


def __rx_stats(modulation=None):
    global rx_res
    global rx_avg
    global rx_cnt
    re_NbFPERThr = re.compile('Num. of frames: (.*), PER \(x10e4\): (.*), Throughput: (.*)Kbps/s*')
    re_Timestamp = re.compile('Timestamp: (.*)us')
    re_modulation = re.compile('\s*(\d+\w|\w+\d)\s*([-]*\d*)\s*([-]*\d*)\s*([-]*\d*)\s*([-]*\d*)\s*([-]*\d*)')
    lines = pi("wlan sudo cat /sys/kernel/debug/ieee80211/" + pds_env['PHY'] + "/wfx/rx_stats")
    return_val = 0
    for line in lines.split('\n'):
        stamp = re_Timestamp.match(line)
        if stamp is not None:
            Timestamp = int(stamp.group(1))
            if Timestamp == 0:
                break
            if Timestamp == rx_res['global']['last_us']:
                break
            else:
                return_val = 1
            rx_res['global']['last_us'] = Timestamp
            rx_res['global']['deltaT'] = (Timestamp - rx_res['global']['start_us'])%pow(2,31)
            if rx_res['global']['loops'] == 0:
                rx_res['global']['start_us'] = (Timestamp - 1000000)%pow(2,31)
            rx_res['global']['loops'] += 1
        cumulated = re_NbFPERThr.match(line)
        if cumulated is not None and int(cumulated.group(1)) > 0:
            rx_res['global']['frames']    += int(cumulated.group(1))
            rx_res['global']['errors']    += __errors_from_per(cumulated.group(1), cumulated.group(2))
            rx_res['global']['PER']        = __per(rx_res['global']['frames'], rx_res['global']['errors'])
            rx_res['global']['Throughput'] = int(cumulated.group(3))
        modline = re_modulation.match(line)
        if modline is not None and int(modline.group(2)) > 0:
            Modulation = modline.group(1)
            rx_res[Modulation]['frames'] += int(modline.group(2))
            rx_res[Modulation]['errors'] += __errors_from_per(modline.group(2), modline.group(3))
            rx_res[Modulation]['PER']  = __per(rx_res[Modulation]['frames'], rx_res[Modulation]['errors'])
            index = 4
            for item in rx_averaging:
                rx_cnt[Modulation][item] += 1
                rx_avg[Modulation][item] += int(modline.group(index))
                rx_res[Modulation][item] = __average(rx_avg[Modulation][item], rx_cnt[Modulation][item])
                index += 1
    return return_val


def rx_logs(mode=None):
    global rx_res
    res = []
    if mode is None:
        for mode in (['global'] + rx_modulations):
            res.append(str.format("mode %7s  %s\n" % (mode, rx_logs(mode))))
        return ''.join(res).strip()
    mode = 'global' if mode not in rx_modulations else mode
    keys = rx_globals if mode == 'global' else rx_items
    for key in keys:
        res.append(str.format("%s %5s  " % (key, str(rx_res[mode][key]))))
    return ''.join(res).rstrip()


def rx_receive(mode='global', frames=1000, timeout_s=0, sleep_ms=750):
    global rx_res
    global rx_job
    start = time.time()
    __rx_clear()
    nb_pkt = nb_same_timestamp = 0
    if mode == 'endless':
        if rx_job is not None:
                rx_job.stop()
        rx_job = Job(750, __rx_stats, 'global')
        rx_job.start()
        return "Endless rx loop started. Use 'rx_logs()' to monitor Rx, 'rx_kill()' to stop Rx monitoring, 'rx_stop()' to stop Rx entirely"
    mode = 'global' if mode not in rx_modulations else mode
    while nb_pkt < frames:
        time.sleep(sleep_ms/1000.0)
        Timestamp_changed = __rx_stats()
        elapsed = time.time() - start
        if Timestamp_changed != 0:
            nb_same_timestamp = 0
            print(str.format(' >>> rx_receive:   mode %s %s   (%5.2f s)' % (mode, rx_logs(mode), elapsed)))
            nb_pkt = rx_res[mode]['frames']
        else:
            nb_same_timestamp += 1
            if nb_same_timestamp > 3:
                msg = ' Error: Rx stats timestamp not changing. Rx not running!'
                add_pds_warning(msg)
                print('\n', msg, '\n')
                break
        if timeout_s > 0 and elapsed > timeout_s:
                msg = str.format(' Warning: Rx stats timeout after %5.2f seconds!' , (str(elapsed)) )
                add_pds_warning(msg)
                print('\n', msg, '\n')
                break
    return rx_logs(mode)


def rx_kill():
    """ Killing 'endless' Rx monitoring loop """
    if rx_job is not None:
            rx_job.stop()


def __rx_clear():
    global rx_res
    global rx_avg
    global rx_cnt
    rx_res = {}
    rx_avg = {}
    rx_cnt = {}
    for mode in rx_modulations:
        dict_items = {}
        for item in rx_items:
            dict_items[item] = __per() if item == 'PER' else 0
        rx_res[mode] = dict_items
        cnt_items = {}
        avg_items = {}
        for item in rx_averaging:
            avg_items[item] = 0
            cnt_items[item] = 0
        rx_avg[mode] = avg_items
        rx_cnt[mode] = cnt_items
    for mode in ['global']:
        dict_items = {}
        for item in rx_globals:
            dict_items[item] = __per() if item == 'PER' else 0
        rx_res[mode] = dict_items


rx_modulations = [
    '1M', '2M', '5.5M', '11M',
    '6M', '9M', '12M', '18M', '24M', '36M', '48M', '54M',
    'MCS0', 'MCS1', 'MCS2', 'MCS3', 'MCS4', 'MCS5', 'MCS6', 'MCS7']
rx_items = ['frames', 'errors', 'PER', 'RSSI', 'SNR', 'CFO']
rx_averaging= ['RSSI', 'SNR', 'CFO']
rx_globals = ['frames', 'errors', 'PER', 'Throughput', 'deltaT', 
              'loops', 'start_us', 'last_us']
rx_job = None

__rx_clear()


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

    print(tx_stop())

