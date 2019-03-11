#!/usr/bin/python3
# -*- coding: utf-8 -*-

from time import sleep

from wfx_test_functions import *
from wfx_pds_tree import *


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

    pi(wlan_name + " " + "sudo wfx_driver_reload -C")
    sleep(0.5)
    wf200_fw = fw_version("refresh")

    _pds.fill_tree(wf200_fw)

    pi("wlan pi_traces on")
    pi("wlan pds_traces off")

    print("Driver reloaded, FW" + wf200_fw)
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

    print(pds.pretty())
