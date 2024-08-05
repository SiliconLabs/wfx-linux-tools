This repository is designed to be used from a custom Raspberry Pi image that can be downloaded using the links below (click on the versions in the 'SD Card' column of the table).


Releases
========

| SD Card download                                                                                                                              | kernel       | Raspbian      | wfx-linux-driver | wfx-firmware | wfx-linux-tools | RPi 2B  | RPi 3B | RPi 3B+ | RPi 4B 2GB | RPi 4B 8GB |
|-----------------------------------------------------------------------------------------------------------------------------------------------|--------------|---------------|------------------|--------------|-----------------|---------|--------|---------|------------|------------|
| [5.2](https://webftp.silabs.com/download?domain=silabs.com&id=bc79809712594c76bb31643cbafe3612-771664b71a7b487b946282bd8bf7746c)              | 5.15.32-v7+  | 11 (bullseye) | 2.13.2-public    | FW3.16.0     | 5.2               | yes     | yes    | yes     | yes        | possible/untested due to RPi unavailability |
| 5.1 (Deprecated)              | 5.15.32-v7+  | 11 (bullseye) | 2.13.2-public    | FW3.15.0     | 5.1.5             | yes     | yes    | yes     | yes        | possible/untested due to RPi unavailability |
| 3.3 (Deprecated)              | 4.19.57-v7l+ | 10 (buster)   | 2.5.2-public     | FW3.9.1      | 3.3             | yes     | yes    | yes     | yes        | no         |
| 3.2 (Deprecated)              | 4.19.57-v7l+ | 10 (buster)   | 2.3.5-public     | FW3.3.2      | 3.2             | yes     | yes    | yes     | yes        | no         |
| 3.1 (Deprecated)              | 4.19.57-v7l+ | 10 (buster)   | 2.2.5-public     | FW3.1.1      | 3.1             | yes     | yes    | yes     | yes        | no         |
| 2.2 (Deprecated)              | 4.4.50-v7+   | 8 (jessie)    | 2.1.2-public     | FW2.2.2      | 2.2             | yes     | yes    | no      | no         | no         |
| 2.1 (Deprecated)                                                                                                                              | 4.4.50-v7+   | 8 (jessie)    | 2.0-public       | FW2.0.0      | 2.1             | yes     | yes    | no      | no         | no         |

Note: The **download password** for all images is: **`D3fault_password`**

Copy image
==========

To copy the image on an SD card, use [Etcher](https://etcher.io/).
The detailed procedure is available in [Raspberry Pi official documentation](https://www.raspberrypi.org/documentation/installation/installing-images/README.md), section “Writing an image to the SD card”.
