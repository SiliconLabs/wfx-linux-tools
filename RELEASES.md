This repository is designed to be used from a custom Raspberry Pi image that can be downloaded using the links below (click on the versions in the 'SD Card version' column of the table).


Releases
========

NB: The download password for ALL releases is now: `D3fault_password`


| SD Card version | kernel     | Debian | Raspbian   | wfx-linux-driver | wfx-firmware | wfx-linux-tools | RPi 2B  | RPi 3B | RPi 3B+ |
|-----------------|------------|--------|------------|------------------|--------------|-----------------|-------- |--------|---------|
| [2.1](https://webftp.silabs.com/download?domain=silabs.com&id=063a89e1b8b346be901fcce7b2978ded-7be97ccde747472583d37176e11cf136)                           | 4.4.50-v7+ | 8.0    | 8 (jessie) | 2.0-public       | FW2.0.0      | 2.1             | yes     | yes    | no (*)  | 
| [1.0](https://webftp.silabs.com/download?domain=silabs.com&id=92a1439336474a1783398737dd38d86d-27e4863b12ca42b4aa0268188a29e1ae) (deprecated)      | 4.4.50-v7+ | 8.0    | 8 (jessie) | 1.6-public       | FW1.2.15     | 1.0             | yes     | yes    | no (*)  | 
 
(*) Rpi 3B+ support can be achieved by some magic (TBD)


Copy image
==========

To copy the image on an SD card, use [Etcher](https://etcher.io/).
The detailled procedure is available in [Raspberry Pi official documentation](https://www.raspberrypi.org/documentation/installation/installing-images/README.md), section “Writing an image to the SD card”.
