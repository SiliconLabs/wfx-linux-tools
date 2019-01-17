wfx-linux-tools
===============

Contents
--------

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
