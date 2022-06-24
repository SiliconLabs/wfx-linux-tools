This repository is designed to be used from a custom Raspberry Pi image that can be downloaded using the links below (click on the versions in the 'SD Card' column of the table).


Releases
========

| SD Card download                                                                                                                              | kernel       | Raspbian      | wfx-linux-driver | wfx-firmware | wfx-linux-tools | RPi 2B  | RPi 3B | RPi 3B+ | RPi 4B 2GB | RPi 4B 8GB |
|-----------------------------------------------------------------------------------------------------------------------------------------------|--------------|---------------|------------------|--------------|-----------------|---------|--------|---------|------------|------------|
| [5.1](https://webftp.silabs.com/download?domain=silabs.com&id=badaf7173d8a479da68c013e5eacff09-206e32f926d6437183cd1c2ae1e2950d)              | 5.15.32-v7+  | 11 (bullseye) | 2.13.2-public    | FW3.15.0     | 5.1.5             | yes     | yes    | yes     | yes        | possible/untested due to RPi unavailability |
| [3.3](https://webftp.silabs.com/download?domain=silabs.com&id=0194fe1deab34488b8bf408b565c55d4-adf871089fb84f889ba40fcb389d339d)              | 4.19.57-v7l+ | 10 (buster)   | 2.5.2-public     | FW3.9.1      | 3.3             | yes     | yes    | yes     | yes        | no         |
| [3.2](https://webftp.silabs.com/download?domain=silabs.com&id=a653cfa624a74988858d39ac03f883e3-c58350d890da40a1a176106001ef0a51)              | 4.19.57-v7l+ | 10 (buster)   | 2.3.5-public     | FW3.3.2      | 3.2             | yes     | yes    | yes     | yes        | no         |
| [3.1](https://webftp.silabs.com/download?domain=silabs.com&id=b08821bb776b4ffa840c8196693a92a3-178d227fe0444c0fb30db4ca648b0dab)              | 4.19.57-v7l+ | 10 (buster)   | 2.2.5-public     | FW3.1.1      | 3.1             | yes     | yes    | yes     | yes        | no         |
| [2.2](https://webftp.silabs.com/download?domain=silabs.com&id=e23f672704b44979b4b5af485d9d0fc2-fef78eaac48d40c482e759d0bf1d705b)              | 4.4.50-v7+   | 8 (jessie)    | 2.1.2-public     | FW2.2.2      | 2.2             | yes     | yes    | no      | no         | no         |
| 2.1 (deprecated)                                                                                                                              | 4.4.50-v7+   | 8 (jessie)    | 2.0-public       | FW2.0.0      | 2.1             | yes     | yes    | no      | no         | no         |

Note: The **download password** for all images is: **`D3fault_password`**

Copy image
==========

To copy the image on an SD card, use [Etcher](https://etcher.io/).
The detailed procedure is available in [Raspberry Pi official documentation](https://www.raspberrypi.org/documentation/installation/installing-images/README.md), section “Writing an image to the SD card”.
