# wfx_test
*wfx_test* is a set of python3 scripts allowing RF testing

## [Updating this tool](#updating)
```
cd /home/pi/siliconlabs/wfx-linux-tools/test-feature
git fetch
git checkout origin/master
```

## [Typical Use Case](#typical-use-case)
### Tx
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
NB: The last 2 lines correspond to the `stop()` call, which is sending 100 frames<br>
NB: `dmesg_period()` allows controlling the delay between these messages

### Rx
```
cd /home/pi/siliconlabs/wfx-linux-tools/test-feature
python3
>>> from wfx_test import *
>>> pds = init_board()
>>> tx_rx_select(1,1)
>>> channel(11)
>>> rx_start()
>>> rx_receive('MCS7', frames=10000, timeout = 10)
>>> rx_logs('global')
>>> rx_logs('MCS7')
>>> rx_logs()
. . .
>>> rx_stop()
```
While testing, an rx_stats indication message is updated by the FW every 1000 ms,
 and copied by the driver under `/sys/kernel/debug/ieee80211/phy0/wfx/rx_stats`.
This content is polled by `rx_receive()`, results are accumulated and averaged internally
 Those results are retrieved by the user using `rx_logs()`
```
>>> rx_logs('global')
frames   588  errors   116  PER 1.973e-01  Throughput    78  deltaT 10000057  loops    10  start_us 2245737  last_us 12245794
>>> rx_logs('24M')
frames    76  errors    48  PER 6.316e-01  RSSI   -79  SNR     7  CFO   -18
>>> rx_logs():
mode  global  frames   588  errors   116  PER 1.973e-01  Throughput    78  deltaT 10000057  loops    10  start_us 2245737  last_us 12245794
mode      1M  frames   457  errors    14  PER 3.063e-02  RSSI   -77  SNR    10  CFO   -28
mode      2M  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    5.5M  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode     11M  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode      6M  frames     4  errors     3  PER 7.500e-01  RSSI   -78  SNR     8  CFO   -22
mode      9M  frames    10  errors    10  PER 1.000e+00  RSSI   -82  SNR     3  CFO    34
mode     12M  frames     9  errors     9  PER 1.000e+00  RSSI   -83  SNR     5  CFO    19
mode     18M  frames     5  errors     5  PER 1.000e+00  RSSI   -83  SNR     7  CFO    18
mode     24M  frames    76  errors    48  PER 6.316e-01  RSSI   -79  SNR     7  CFO   -18
mode     36M  frames     4  errors     4  PER 1.000e+00  RSSI   -76  SNR     9  CFO   -22
mode     48M  frames     7  errors     7  PER 1.000e+00  RSSI   -84  SNR     2  CFO    -2
mode     54M  frames     7  errors     7  PER 1.000e+00  RSSI   -84  SNR     2  CFO   -27
mode    MCS0  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS1  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS2  frames     1  errors     1  PER 1.000e+00  RSSI   -80  SNR     9  CFO   -20
mode    MCS3  frames     8  errors     8  PER 1.000e+00  RSSI   -80  SNR     9  CFO   -23
mode    MCS4  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS5  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS6  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS7  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
```
NB: PER values above are only considering received packets, not lost packets.
To get a PER taking into account the lost packets it is necessary to compute 
the total number of packets for each mode using the deltaT value 
from `rx_logs('global')`, based on the ideal throughput for the mode.

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
* `rx_start()`                       : Starts receiving frames (all modulations)
* `rx_stop()`                        : Calls tx_stop() to stop receiving
* `rx_receive(mode, frames, sleep_ms, timeout)` : Clear Rx logs and polls FW info (updated every 1000 ms) until it has received the required number of frames
* `rx_logs(mode)`                    : Retrieves Rx logs. Full table if no argument, otherwise only the row matching the 'mode'

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
| `tx_backoff`   |`mode_802_11`:<br>'[B, CCK, DSS]\_[1, 2, 5_5, 11]Mbps'<br>'[G, LEG]\_[6, 9, 12, 18, 24, 36, 48, 54]Mbps'<br>'[MM, GF]\_MCS[0-7]'<br>Examples: 'B_1Mbps', 'LEG_54Mbps', 'GF_MCS5'<br>`backoff_level`: [0:63.75] dB|`BACKOFF_VAL`|
| `tx_framing`   |`packet_length_bytes`:[25-4091] Frame size in bytes\(without CRC\)<br>`delay_between_us`:[0-255] Interframe spacing in us|`FRAME_SIZE_BYTE` |
| `tx_mode`      |`mode_802_11`:<br>'[B, CCK, DSS]\_[1, 2, 5_5, 11]Mbps'<br>'[G, LEG]\_[6, 9, 12, 18, 24, 36, 48, 54]Mbps'<br>'[MM, GF]\_MCS[0-7]'<br>Examples: 'B_1Mbps', 'LEG_54Mbps', 'GF_MCS5'|`HT_PARAM`<br>`RATE`|
| `tx_power`     |`dbm`: [TBD]                                                                  |`MAX_OUTPUT_POWER_QDBM`                   |
| `tx_rx_select` |`tx_ant`: [1-2] Tx antenna<br>`rx_ant`: [1-2] Rx antenna                      |`RF_PORTS`                                |
| `tx_start`     |`nb_frames`: [0-65535] or 'continuous'. Nb of frames to send before stopping. |`NB_FRAME`                                |
| `tx_stop`      |**none**|`NB_FRAME` |
| `regulatory_mode` | `reg_mode`:<br>'[All, FCC, ETSI, JAPAN, Unrestricted]'                    | `REG_MODE`                            |
| `add_tmp_param`|`version`: min FW, `path`: position in tree, `key`: name, `default`:value       | `key` (as entered)                       |
| `dmesg_period` |`period`:[0-TBD/65535?] delay in ms between messages                          |`TEST_IND`                                |
| `rx_start`     |**none**                                                                        |`TEST_MODE`                               |
| `rx_stop`      |**none**                                                                        |`NB_FRAME`                                |
| `rx_receive`   |`mode`: <br>'global'(default if '')<br>'[1, 2, 5.5, 11, 6, 9, 12, 18, 24, 36, 48, 54]M'<br>'MCS[0-7]'<br>`frames`: Nb of frames to receive before stopping'<br>`sleep_ms`:[(750)]. Polling period. No need to poll too often, the FW updates the table only every second<br>`timeout`: max number of seconds to poll (useful if very few frames are received) |**none**|
| `rx_logs`      |`mode`: <br>'global'(default if '')<br>'[1, 2, 5.5, 11, 6, 9, 12, 18, 24, 36, 48, 54]M'<br>'MCS[0-7]'|**none**|


### Rx testing


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

## Advanced features

### Accessing a PDS parameter if it's not managed by a test function

All parameters (even those not managed by test functions) listed in the [test API](https://github.com/SiliconLabs/wfx-linux-tools/tree/master/test-feature#API)
are still accessible using generic functions:

**Reading**
```
wfx_get_list({'NB_FRAME'})
wfx_get_list({'TEST_MODE','NB_FRAME'})
```
 
**Writing** (without sending PDS data)
 
```
wfx_set_dict({'NB_FRAME':12}, 0)
wfx_set_dict({'TEST_MODE':'tx_packet','NB_FRAME':12}, 0)
```

**Writing**(sending PDS data)
```
wfx_set_dict({'NB_FRAME':12}, 1)
wfx_set_dict({'TEST_MODE':'tx_packet','NB_FRAME':12}, 1)
```

### Adding a temporary PDS test parameter

It is always possible to define new parameters and access them using the generic `wfx_get_list` / `wfx_set_dict` functions described above.

**Adding a PDS parameter

```
add_tmp_param('version', 'path', 'key', 'default')
```
adds a (temporary) parameter to the PDS structure. This is useful to test FW release candidates in the lab
example:

```
# Creating the params in the tree (Pending FW support for 'z.a.b.x' &  'z.a.b.y'):
PdsTree.add_tmp_param(pds, '2.0', 'z.a.b', 'x', '10')
PdsTree.add_tmp_param(pds, '2.0', 'z.a.b', 'y', '25')

# Setting the value and sending PDS data:
wfx_set_dict({'x':15, 'y':32}, 1)
```
