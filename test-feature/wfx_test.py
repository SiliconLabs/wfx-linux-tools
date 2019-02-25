#!/usr/bin/python3
import sys

sys.path.insert(0, '/home/pi/siliconlabs/wfx-firmware/PDS/test-resources/')

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
    print("wf200_fw " + wf200_fw)

    definitions_files = pi(wlan_name + " " + "ls " + pds_env['PDS_DEFINITION_ROOT'] + \
         " | grep 'definitions-.*.in'").split("\n")
    definitions_versions = []
    for i in definitions_files:
        definitions_versions.append(i.replace("definitions-","").replace(".in",""))
    template_files = pi(wlan_name + " " + "ls " + pds_env['PDS_TEMPLATE_ROOT'] + " | grep 'template-.*.in'").split("\n")
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
                pds_definitions_file_path = pds_env['PDS_DEFINITION_ROOT'] + "definitions-" + template + ".in"
                pds_template_file_path = pds_env['PDS_TEMPLATE_ROOT'] + "template-" + template + ".pds.in"
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
