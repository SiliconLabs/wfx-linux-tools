#!/usr/bin/python3

from procs_wlan import *
from distutils.version import StrictVersion

wf200_fw = ""


def fw_version():
    res = pi("wf200 sudo wfx_show | grep 'Firmware loaded version:'")
    fw_label = res.split(':')[1].strip()
    return fw_label


def init_board(wlan_name="wf200"):
    """ Called to restart from a fresh copy of the template,
         after reloading the firmware.
        1- reload driver (hence reload FW & PDS data from /lib/firmware)
        2- retrieve current FW version
        3- select 'highest version for this fw' templates
        4- generate the current .pds.in file based on the selected
            definitions and template
    """
    global wf200_fw

    pi("wlan pi_traces  on")
    pi("wlan pds_traces on")

    pi(wlan_name + " " + "sudo wfx_driver_reload -C")
    wf200_fw = fw_version()
    print("wf200_fw " + wf200_fw)

    PDS_path = pds_env['PDS_ROOT']

    definitions_files = pi(wlan_name + " " + "ls " + PDS_path + " | grep 'definitions-.*.in'").split("\n")
    definitions_versions = []
    for i in definitions_files:
        definitions_versions.append(i.replace("definitions-","").replace(".in",""))
    template_files = pi(wlan_name + " " + "ls " + PDS_path + " | grep 'template-.*.in'").split("\n")
    template_versions = []
    for i in template_files:
        template_versions.append(i.replace("template-","").replace(".pds.in",""))
    definitions_versions.sort(key=StrictVersion)
    template_versions.sort(key=StrictVersion)

    pds_definitions_file_path = ""
    pds_template_file_path = ""
    for template in template_versions:
        if StrictVersion(template) <= StrictVersion(wf200_fw):
            if template not in definitions_versions:
                print("WARNING: PDS template " + template + " has no matching definitions file!")
            else:
                pds_definitions_file_path = PDS_path + "definitions-" + template + ".in"
                pds_template_file_path = PDS_path + "template-" + template + ".pds.in"
                last_valid_template = template
        else:
            break

    file_info = "Firmware version " + wf200_fw + "   File created based on " + last_valid_template + " files"

    pds_definitions_file = open(pds_definitions_file_path)
    pds_definitions_data = pds_definitions_file.read()
    pds_definitions_file.close()

    pds_template_file = open(pds_template_file_path)
    pds_template_data = pds_template_file.read()
    pds_template_file.close()

    pds_current_file = open(pds_env['PDS_CURRENT_FILE'], 'w')
    pds_current_file.write("/* " + file_info + " */\n")
    pds_current_file.write("/* Definitions: " + pds_definitions_file_path + "  */\n")
    pds_current_file.write("/* Template:    " + pds_template_file_path + " */\n")
    pds_current_file.write(pds_definitions_data + "\n" + pds_template_data)
    pds_current_file.close()

    pi("wlan pi_traces off")
    pi("wlan pds_traces off")

    return "Driver reloaded, " + pds_env['PDS_CURRENT_FILE'] + " " + file_info


def channel(ch=None):
    if ch is None:
        return "TEST_CHANNEL" + " " + set_pds_param("TEST_CHANNEL")
    else:
        if ch >= 14:
            set_pds_param("TEST_CHANNEL", 14)
        else:
            set_pds_param("TEST_CHANNEL", ch)
    apply_pds()


def tx_power(dbm=None):
    if wf200_fw == "2.0.0":
        if dbm is None:
            power = int(set_pds_param("MAX_OUTPUT_POWER_QDBM"))
            return "MAX_OUTPUT_POWER_QDBM" + " " + str(power) + \
                "  tx_power " + str(int(power/4)) + " dBm"
        else:
            set_pds_param("MAX_OUTPUT_POWER_QDBM", int(4*dbm))
    elif wf200_fw == "1.2.15" or wf200_fw == "1.2.16":
        if dbm is None:
            ofdm = int(set_pds_param("OFDM"))
            cck_dsss = int(set_pds_param("CCK_DSSS"))
            return \
                "OFDM " + str(ofdm) + "  " + \
                "ofdm " + str(int(ofdm/4)) + " dBm" + \
                "CCK_DSSS " + str(cck_dsss) + "  " + \
                "cck_dsss " + str(int(cck_dsss/4)) + " dBm"
        else:
            set_pds_param("OFDM", int(4*dbm))
            set_pds_param("CCK_DSSS", int(4*dbm))
    apply_pds()


def tx_backoff(mode_802_11=None, backoff_level=0):
    if backoff_level == "":
        backoff_level = 0
    if mode_802_11 == "RSVD":
        return
    if mode_802_11 is None:
        backoff_val= set_pds_param("BACKOFF_VAL")
        (backoff_data, nb) = re.subn('\[|\]| ','',backoff_val)
        backoff_max = max(backoff_data.split(','))
        backoff_dbm = str(int(int(backoff_max)/4))
    if StrictVersion(wf200_fw) >= StrictVersion("2.0.0"):
        if mode_802_11 is None:
            return "BACKOFF_VAL " + backoff_max + "  tx_backoff " + \
            backoff_dbm + " dB"
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
            set_pds_param("BACKOFF_VAL", str(value))
    elif StrictVersion(wf200_fw) >= StrictVersion("1.2.15"):
        if mode_802_11 is None:
            return "HT_PARAM    " + set_pds_param("HT_PARAM") + "  " + \
                   "MOD         " + set_pds_param("MOD") + "  " + \
                   "BACKOFF_VAL " + backoff_max + "  tx_backoff " + \
                   backoff_dbm + " dB"
        else:
            res = re.findall("([^_]*)_(.*)", mode_802_11)
            prefix = res[0][0]
            suffix = res[0][1]
            print("mode:" + mode_802_11 + " - prefix:" + prefix + 
                    " - suffix:" + suffix)
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
            print("HT_PARAM:" + ht_param + " - MOD:" + rate + 
                    " - BACKOFF_VAL:" + backoff_level)
            set_pds_param("HT_PARAM", ht_param)
            set_pds_param("MOD", rate)
            set_pds_param("BACKOFF_VAL", int(4 * backoff_level))
    else:
        return "PDS format unknown for " + wf200_fw + "Firmware version"
    apply_pds() 


def tx_rx_select(tx_ant=None, rx_ant=None):
    if tx_ant is None:
        return "RF_PORTS" + " " + set_pds_param("RF_PORTS")
    else:
        set_pds_param("RF_PORTS", "TX" + str(tx_ant) + \
                                 "_RX" + str(rx_ant))
    apply_pds() 


def tx_stop():
    set_pds_param("NB_FRAME", 100)
    apply_pds() 


def tx_framing(packet_length_bytes=1000, delay_between_us=100):
    if packet_length_bytes is None:
        return "FRAME_SIZE_BYTE " + set_pds_param("FRAME_SIZE_BYTE") + \
             "  " + "IFS_US " + set_pds_param("IFS_US")
    else:
        set_pds_param("FRAME_SIZE_BYTE", packet_length_bytes)
        set_pds_param("IFS_US", delay_between_us)


def tx_mode(mode_802_11=None):
    if mode_802_11 is None:
        return "HT_PARAM " + set_pds_param("HT_PARAM") + "  " + \
               "RATE " + set_pds_param("RATE")
    else:
        res = re.findall("([^_]*)_(.*)", mode_802_11)
        prefix = res[0][0]
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
        set_pds_param("HT_PARAM", ht_param)
        set_pds_param("RATE", rate)


def tx_start(nb_frames=None):
    if nb_frames is None:
        return "TEST_MODE " + set_pds_param("TEST_MODE") + "  " + \
               "NB_FRAME "  + set_pds_param("NB_FRAME")
    else:
        set_pds_param("TEST_MODE", "tx_packet")
        if str(nb_frames) is "continuous":
            set_pds_param("NB_FRAME", "0")
        else:
            set_pds_param("NB_FRAME", nb_frames)
    apply_pds()


def tone(cmd, freq=0):
    # CW Mode: generate CW @ (freq+1)*312.5Khz
    if cmd == "start":
        set_pds_param("CW_MODE", "single")
        set_pds_param("TEST_MODE", "tx_cw")
        set_pds_param("FREQ1", freq)
    elif cmd == "stop":
        set_pds_param("TEST_MODE", "tx_packet")
        set_pds_param("NB_FRAME", 100)
    apply_pds()


def tone_power(dbm=None):
    if dbm is None:
        power = int(set_pds_param("MAX_OUTPUT_POWER"))
        return "MAX_OUTPUT_POWER " + str(power) + "  " + \
                "  tone_power " + str(int(power/4)) + " dBm"
    else:
        set_pds_param("MAX_OUTPUT_POWER", int(4*dbm))
    apply_pds() 