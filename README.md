Silicon Labs WFX Raspberry Pi Documentation
===========================================

This guide is meant to be read after the WF200 Quick Start Guide (qsg166-wf200-wifi-devkit.pdf from https://www.silabs.com/).
It covers steps needed to develop on a Raspberry Pi with a WFX EXP after trying basic Wi-Fi demos.
All this documentation assumes that the Raspberry Pi is running the latest image from the [releases page](RELEASES.md)

**WARNING: CHANGE THE HOSTNAME BEFORE CONNECTING THE RASPBERRY PI TO A NETWORK**

Changing the hostname
---------------------
If two machines have the same hostname on a network, it becomes hard to tell which one we connect to.
This can happen if two Raspberries with the same SD card image are plugged on the same network.
To be sure this issue will not happen, it is *strongly recommended* to change the hostname just after running the Quick Start Guide demos.

From a shell on the Raspberry (either directly or through a SSH client like PuTTY or MobaXterm):
 1. Run `sudo raspi-config`
 2. Select `Hostname`
 3. Choose a meaningfull, unique, hostname like pi-\<your place\>-\<your login name\>
 4. Reboot
 5. If connected through SSH, change the hostname in the SSH client session.

Connecting to a network
-----------------------
Once hostname has been change, it is possible to plug the Raspberry Pi on a DHCP capable network.
Then, just use SSH with the configured hostname (user is `pi`) to access the board.

Stand alone use
---------------
The Raspberry Pi can also be used directly like a PC, with a keyboard, mouse and screen plugged to it. This can be useful for troubleshooting network issue.

Bus change
----------
By default, the Raspberry Pi is configured to use SDIO.
To change to SPI, run `wfx_bus --set spi`. For checking bus mode, use `wfx_bus --show`.
Do not forget to reboot after a bus change.

Repository contents
-------------------
 - `demos/` mainly hosts two scripts (`wfx_demo_station` and `wfx_demo_ap`) that
   can be used to test the Wi-Fi. These scripts contain the usual commands for
   setting up basic station and access point so it is possible to use them as
   reference for custom application, in this case, first copy the script
   outside of the repository (e.g. `/home/pi/custom_scripts`) to avoid issue when
   updating the repository.

 - `examples/` contains an example for a custom PDS file.

 - `overlays/` contains specific device tree overlays for the Raspberry Pi.

 - `scripts/` contains tools to configure and install WF200. Each script's
   documentation is accessible with `--help` option or at the top of the file.

 - `update/` contains tools to update the SD card on which it is supposed to be
   installed.

 - `pds_compress/` contains tool to process PDS files.
