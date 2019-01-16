#!/usr/bin/python3

import subprocess
import sys
import re


pds_env = dict()
pds_env['TEST_FEATURE_ROOT'] = "/home/pi/siliconlabs/wfx-linux-tools/test-feature/"
pds_env['PDS_ROOT'] = pds_env['TEST_FEATURE_ROOT'] + "PDS/"
pds_env['PDS_CURRENT_FILE'] = "/tmp/current_pds_data.in"
pds_env['SEND_PDS_FILE'] = "/sys/kernel/debug/ieee80211/phy0/wfx/send_pds"

pi_traces = 1
pds_traces = 1

def set_pds_param(param, value=""):
    global pi_traces
    global pds_traces
    pds_current_file = open(pds_env['PDS_CURRENT_FILE'])
    pds_current_data = pds_current_file.read()
    pds_current_file.close()
    group1 = '(\n\s*[^/]\s*)'
    group2 = '(' + param + '\s*:\s*)'
    group3 = '(\[.*\]|\w*)'
    group4 = '(,)?'
    current_value = re.search(group1 + group2 + group3 + group4, pds_current_data)
    if current_value:
        if str(value) is "":
            return str(current_value.group(3))
        else:
            # Replace current value for PARAM by new value
            (new_pds_data, nb) = re.subn(group1 + group2 + group3 + group4, '\g<1>' + '\g<2>' + str(value) + '\g<4>', pds_current_data)
            if nb > 0:
                pds_current_file = open(pds_env['PDS_CURRENT_FILE'], 'w')
                pds_current_file.write(new_pds_data)
                pds_current_file.close()
                new_value = re.search(group1 + group2 + group3 + group4, pds_current_data)
                result_string = str(param) + " " + str(new_value.group(3))
                if pds_traces:
                    print(result_string)
                return result_string
            else:
                print("Error: set_pds_param: no re.subn match for '" + param + "'!")
    else:
        print("set_pds_param: No match for '" + param + "' in " + pds_env['PDS_CURRENT_FILE'] + "!")


def apply_pds():
    global pds_traces
    result_string = pi("wf200 sudo pds_compress " + pds_env['PDS_CURRENT_FILE'] + " 2>&1")
    if ":error:" in result_string:
        print("WARNING: No pds data sent! " + result_string)
    else:
        if pds_traces:
            print("      " + pi("wf200 sudo pds_compress " + pds_env['PDS_CURRENT_FILE']))
        pi("wf200 sudo pds_compress " + pds_env['PDS_CURRENT_FILE'] + " " + pds_env['SEND_PDS_FILE'])


def pi(args):
    global pi_traces
    global pds_traces

    split_args = args.split(' ')
    if len(split_args) == 0:
        return "procs_wlan.pi: no arguments?"
    target = split_args[0]
    if len(split_args) <= 1:
        return "procs_wlan.pi: no arguments for target " + target + "?"
    cmd = split_args.copy()
    del cmd[0]
    cmd_args = cmd.copy()
    del cmd_args[0]
    if target in "Hello":
        return "Hi!"
    if target in "wf200 wlan":
        if cmd[0] in ["help"]:
            return "Available " + target + \
                   " commands:\n      traces <on/off>\n      write\n      read\n" + \
                   "      accessmode\n      copyfile\n      testmode\n      kernel\n"
        elif cmd[0] in ["pi_traces"]:
            if len(cmd) > 1:
                if cmd[1] == "on":
                    pi_traces = 1
                if cmd[1] == "off":
                    pi_traces = 0
            return "procs_wlan.pi: pi_traces " + str(pi_traces)
        elif cmd[0] in ["pds_traces"]:
            if len(cmd) > 1:
                if cmd[1] == "on":
                    pds_traces = 1
                if cmd[1] == "off":
                    pds_traces = 0
            return "procs_wlan.pi: pds_traces " + str(pds_traces)
        elif cmd[0] in ["kernel"]:
            return pi(target + " " + "uname -a")
        else:
            if pi_traces:
                print("procs_wlan.pi: Execute:  " + ' '.join(cmd))
            op = subprocess.Popen(' '.join(cmd), shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if op:
                output = str(op.stdout.read(), "utf-8").strip()
                if pi_traces:
                    for line in output.split("\n"):
                        print("procs_wlan.pi:  > > > :  " + line)
                return output
            else:
                error = str(op.stderr.read(), "utf-8").strip()
                print("procs_wlan.pi: Error:", error)
                return error
    else:
        return "procs_wlan.pi: Target '" + target + "' not supported\n"


if __name__ == '__main__':
    del sys.argv[0]
    print(pi(' '.join(sys.argv)))
