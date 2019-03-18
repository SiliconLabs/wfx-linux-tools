# wfx_test
*wfx_test* is a set of python3 scripts allowing RF testing

## [Updating this tool](#updating)
```
cd /home/pi/siliconlabs/wfx-linux-tools/test-feature
git fetch
git checkout origin/master
```

## [Typical Use Case](#typical-use-case)
```
cd /home/pi/siliconlabs/wfx-linux-tools/test-feature
python3
>>> from wfx_test import *
>>> pds = init_board()
>>> tx_rx_select(1,1)
>>> channel(11)
>>> tx_mode('GF_MCS0')
>>> tone_power(10)
>>> tx_start('continuous')
. . .
>>> tx_stop()
```
While testing, messages are issued in dmesg every TEST_IND period (in ms):
```
wfx_wlan: Start TX packet test feature
wfx_wlan: TX packet test ongoing...
wfx_wlan: TX packet test ongoing...
. . .
wfx_wlan: End of TX packet test
wfx_wlan: Start TX packet test feature
wfx_wlan: End of TX packet test
```
NB: The last 2 lines correspond to the `stop()` call, which is sending 100 frames
Nb: `dmesg_period()` allows controlling the delay between these messages

## PDS structure
The PDS structure as filled before calling pds_compress is as follows:
```
TEST_FEATURE_CFG : {
        RX :                              { },
        CFG_TX_PACKET : {
                REG_MODE :                        DFS_Unrestricted,
                IFS_US :                          0,
                RATE :                            N_MCS7,
                NB_FRAME :                        0,
                FRAME_SIZE_BYTE :                 3000,
                HT_PARAM :                        MM,
        },
        CFG_TX_CW : {
                FREQ1 :                           1,
                FREQ2 :                           2,
                CW_MODE :                         single,
                MAX_OUTPUT_POWER :                68,
        },
        TEST_IND :                        1000,
        TEST_CHANNEL_FREQ :               11,
        TEST_MODE :                       tx_packet,
},
MAX_TX_POWER_CFG : {
        FRONT_END_LOSS_CORRECTION_QDB :   0,
        MAX_OUTPUT_POWER_QDBM :           80,
        BACKOFF_QDB : [ {
                CHANNEL_NUMBER :                  [1, 14],
                BACKOFF_VAL :                     [0, 0, 0, 0, 0 ,0],
        } ],
        RF_PORT :                         RF_PORT_BOTH,
},
RF_ANTENNA_SEL_DIV_CFG : {
        RF_PORTS :                        TX1_RX1,
},
```

# wfx_test modules details

## wfx_pds_tree module 
wfx_pds_tree.py manages the PDS data in a nested dict

### wfx_pds{} defines the PDS data structure
 * item names are unique by design (FW constraint)
 * `wfx_pds` defines the miminum FW version and default value for each item
 * `wfx_pds` lists possible values for each item
 * `wfx_pds` contains the documentation relative to each item
 

### class PdsTree
 * `set_current_fw_version(version)` : Stores the current FW version (retrieved from HW by upper layers).
 * `fill_tree(version)`              : Fills the tree, adding only items supported by the current FW.
 * `set(key, value)`                 : Sets an item to a new value, wherever it is in the tree.
 * `get(key)`                        : Gets an item value, wherever it is in the tree.
 * `print()`                         : Returns one-line PDS data.
 * `pretty()`                        : Returns tabulated PDS data.
 * `sub_tree(keys)`                  : Returns a copy of the PDS data, with only (entire) sections matching the selected keys. 
 Used to avoid sending entire PDS data on each 'send'.


## wfx_test_core module
wfx_test_core.py provides generic access to system calls and functions to set several PDS items before sending the 
corresponding PDS data to the HW

* `fw_version()`                     : Retrieves the current FW version from dmesg.
* `pi(args)`                         : provides access to wf200 functions (if args start with 'wf200' or 'wlan')
 or system functions otherwise.
* `send(parameters_list)`            : Generates a sub-tree containing only the sections matching the listed items, 
then send it to the pds input file.
* `wfx_get_list(parameters_list)`    : Returns a name/value sequence for all selected items.
* `wfx_set_dict(parameters_dict)`    : Sets all selected items to their desired values & call `send(parameters_list)`.


## wfx_test_functions module (user functions)
wfx_test_functions.py uses wfx_test_core functions to translate user function calls into PDS data and send it.
These are the functions which are primarily used by users to test the product.
When called with no argument, all functions return the corresponding value(s) of the parameters they control.

* `channel(ch)`                      : Sets the test channel.
* `tone(cmd, freq)`                  : Selects between 'cw' (i.e. 'Continuous Wave') or 'packet' transmission modes
 as well as the tone frequency.
* `tone_power(dBm)`                  : Controls the tone power
* `tx_backoff(mod, backoff_level)`   : Sets the backoff level for one group of modulations. 
All other backoff values are set to 0.
* `tx_framing(pkt_len, delay_us)`    : Controls the frame size and IFS (InterFrame Spacing)
* `tx_mode(mode)`                    : Selects between MM (mixed mode) & GF (Greenfield) and sets the rate
* `tx_power(dBm)`                    : Sets the maximum output power
* `tx_rx_select(tx_ant, rx_ant)`     : Selects the Tx/Rx antennas
* `tx_start(nb_frames)`              : Starts sending a selected number of frames. With 0 or 'continuous' = continuous
* `tx_stop()`                        : Sends a burst of 100 frames to complete a previous continuous transmission 

Additional functions
* `add_tmp_param("version", "path", "key", "default")`: Add a (temporary) parameter to the PDs structure. Useful to test FW release candicates in the lab
* `dmesg_period(period)`                              : Controls the delay between indication messages (in dmesg)

## [wfx_test API](#API)
### wfx_test_functions parameters vs PDS parameters

| function       | function parameters                                                          | PDS parameters                           |
|----------------|------------------------------------------------------------------------------|------------------------------------------|
| `channel`      |`ch`: [1-14]\(channel\) or [2300-2530] MHz                                    |`TEST_CHANNEL_FREQ`                       |
| `tone`         |`cmd`: 'start' 'stop'<br>`freq`: offset in 312.5 kHz steps                    |`TEST_MODE`<br>`NB_FRAME`<br>`FREQ1`      |
| `tone_power`   |`dbm`: [TBD]                                                                  |`MAX_OUTPUT_POWER`                        |
| `tx_backoff`   |`mode_802_11`: 'DSSS' '6Mbps' '9Mbps' '12Mbps' '18Mbps' '24Mbps' '36Mbps' '48Mbps' '54Mbps' 'MCS7'<br>`backoff_level`: [0:63.75] dB|`BACKOFF_VAL`|
| `tx_framing`   |`packet_length_bytes`:[25-4091] Frame size in bytes\(without CRC\)<br>`delay_between_us`:[0-255] Interframe spacing in us|`FRAME_SIZE_BYTE` |
| `tx_mode`      |`mode_802_11`: 'GF_' 'MM_' 'LEG_' DSSS_' 'CCK_' followed by rate in Mbps \(1, 2, 5_5, 11, 6, 9, 12, 18, 24, 36, 48, 54\) depending on the mode|`HT_PARAM`<br>`RATE`|
| `tx_power`     |`dbm`: [TBD]                                                                  |`MAX_OUTPUT_POWER_QDBM`                   |
| `tx_rx_select` |`tx_ant`: [1-2] Tx antenna<br>`rx_ant`: [1-2] Rx antenna                      |`RF_PORTS`                                |
| `tx_start`     |`nb_frames`: [0-65535] or 'continuous'. Nb of frames to send before stopping. |`NB_FRAME`                                |
| `tx_stop`      |**none**|`NB_FRAME` |
| `add_tmp_param`|`version`: min FW, `path`: position in tree, `key`: name, `default`:value     | `key` (as entered)                       |
| `dmesg_period` |`period`:[0-TBD/65535?] delay in ms between messages                          |`TEST_IND`                                |

### wfx_test_core functions which may be useful to the user

| function        | function parameters                                                   | Action                                        | Example(s)                                                                            |
|-----------------|-----------------------------------------------------------------------|-----------------------------------------------|---------------------------------------------------------------------------------------|
| `wfx_set_dict`  | dictionary with comma-separated 'parameter': value pairs. `send_data` | Set all parameters to their respective values | wfx_set_dict({"TEST_MODE": "tx_cw", "CW_MODE": "single", "FREQ1": freq}, send_data=1) |
| `wfx_get_list`  | comma-separated list of 'parameter' names                             | Return all parameters current values          | wfx_get_list({"TEST_MODE", "CW_MODE", "FREQ1"})                                       |
| `pi('wlan a b')`| String interpreted by the python code                                 | Manage the wfx test feature                   | pi("wlan pi_traces on"); pi("wlan pds_traces off");                                   |
| `pi('pwd')`     | String interpreted by linux on the Pi                                 | Execute the command on the Pi                 | pi("wfx_troubleshooter --checks"); pi("ls -al --g");                                  |


## Checking the PDS content as it is sent to pds_compress
Edit `/tmp/current_pds_data.in` to check the PDS data

## Enabling/disabling traces

| `pi("wlan pi_traces on")`   | `pi("wlan pi_traces off")`  |
|-----------------------------|-----------------------------|
| `pi("wlan pds_traces on")`  | `pi("wlan pds_traces off")` |

## Printing the current PDS tree content

| pretty (tabulated)    | single line           |
|-----------------------|-----------------------|
| `print(pds.pretty())` | `print(pds.print())`  |

Nb: the above is only possible if using `pds = init_board()`
