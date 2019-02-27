#!/usr/bin/python3
import sys
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--internal', action='store_true',
                    help='(flag) uses internal test path')

args = parser.parse_args()

if args.internal == False:
    sys.path.insert(0, '/home/pi/siliconlabs/wfx-firmware/PDS/test/')
else:
    print("internal mode")
    sys.path.insert(0, '/home/pi/siliconlabs/wfx_pds/test/')
    print("wfx_test           called  from " + os.getcwd())
    print("wfx_test           running from " + os.path.dirname(os.path.abspath(__file__)))


from wfx_test_functions import *
from distutils.version import StrictVersion
from time import sleep

def init_board(wlan_name="wf200"):
    """ Called to restart from a fresh copy of the template,
         after reloading the firmware.
        1- reload driver (hence reload FW & PDS data from /lib/firmware)
        2- retrieve current FW version
        3- select 'highest version for this fw' templates
        4- generate the current .pds.in file based on the selected
            definitions and template
    """

    pi("wlan pi_traces  on")
    pi("wlan pds_traces on")

    pi(wlan_name + " " + "sudo wfx_driver_reload -C")
    sleep(0.5)
    wf200_fw = fw_version("refresh")

    pds_definitions_file_path = pds_env['PDS_DEFINITION_ROOT'] + "definitions.in"
    pds_template_file_path = pds_env['PDS_TEMPLATE_ROOT'] + "wfx_test.pds.in"

    file_info = "Firmware version " + wf200_fw

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
