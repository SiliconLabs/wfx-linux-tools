#!/bin/bash

echo "Current configuration"
. ./wfx_config.sh
echo ""

kernel=$(uname -r)

echo "System:   $(cat /sys/firmware/devicetree/base/model)"
echo "System:   Linux kernel $kernel"

wfx_core_base=/lib/modules/$kernel/kernel/drivers/net/wireless/siliconlabs/wfx/wfx_core.ko
wfx_sdio_base=/lib/modules/$kernel/kernel/drivers/net/wireless/siliconlabs/wfx/wfx_wlan_sdio.ko
wfx_spi_base=/lib/modules/$kernel/kernel/drivers/net/wireless/siliconlabs/wfx/wfx_wlan_spi.ko
wfx_fw_base=/lib/firmware/wfm_wf200.sec
wfx_pds_base=/lib/firmware/pds_wf200.json
wfx_core_conf=/etc/modprobe.d/wfx_core.conf

# if using symbolic links, use the links, otherwise use the files
wfx_core_link=$(readlink $wfx_core_base)
if [ -n "$wfx_core_link" ]; then
	wfx_core_module=$(ls $wfx_core_base)
else
	wfx_core_module=$wfx_core_base
fi

wfx_sdio_link=$(readlink $wfx_sdio_base)
if [ -n "$wfx_sdio_link" ]; then
	wfx_sdio_module=$(ls $wfx_sdio_base)
else
	wfx_sdio_module=$wfx_sdio_base
fi

wfx_spi_link=$(readlink $wfx_spi_base)
if [ -n "$wfx_spi_link" ]; then
	wfx_spi_module=$(ls $wfx_spi_base)
else
	wfx_spi_module=$wfx_spi_base
fi

wfx_fw_link=$(readlink $wfx_fw_base)
if [ -n "$wfx_fw_link" ]; then
	wfx_fw_file=$(ls $wfx_fw_base)
else
	wfx_fw_file=$wfx_fw_base
fi

wfx_pds_link=$(readlink $wfx_pds_base)
if [ -n "$wfx_pds_link" ]; then
	wfx_pds_file=$(ls $wfx_pds_base)
else
	wfx_pds_file=$wfx_pds_base
fi

wfx_power_mode_option=$(cat $wfx_core_conf | grep ^options | grep wfx_power_mode)

missing_files=0

# SDIO test: first of all, check if SDIO overlay is enabled in .boot/config.txt
SDIO_overlay=$(cat /boot/config.txt | grep ^dtoverlay= | grep sdio)
if [ -z "$SDIO_overlay" ]; then
	WFX_SDIO_Overlay_enabled=0
else
	WFX_SDIO_Overlay_enabled=1
	WFX_DRIVER=wfx_wlan_sdio
	echo "User:     WFX SDIO overlay enabled         (in /boot/config.txt)"
	# SDIO detection at boot will only occur if sdio overlay is enabled in boot/config.txt
	if [ "$WFX_SDIO_Overlay_enabled" = 1 ]; then
		# Check if SDIO has been detected at boot, and proceed only if yes
		mmc=$(dmesg | grep "new high speed SDIO card")
		if [ -n "$mmc" ]; then
			echo "Startup:  SDIO Part detected at boot       ($mmc)"
			# Check if SDIO driver is blacklisted
			SDIO_blacklisted=$(cat /etc/modprobe.d/raspi-blacklist.conf | grep ^blacklist | grep wfx_wlan_sdio)
			SDIO_IN_MODULES=$(cat /etc/modules | grep ^wfx_wlan_sdio)
			if [ -z "$SDIO_blacklisted" ]; then
				WFX_SDIO_Driver_blacklisted=0
				if [ ! -z "$SDIO_IN_MODULES" ]; then
					echo "User:     WFX SDIO Driver not blacklisted  (it should load automatically after detection)"
				else
					echo "User:     WFX SDIO Driver not blacklisted but not in /etc/modules (it must be loaded using 'sudo modprobe -v wfx_wlan_sdio')"
				fi
			else
				WFX_SDIO_Driver_blacklisted=1
				echo "User:     WFX SDIO Driver blacklisted      (it must be loaded using 'sudo modprobe -v wfx_wlan_sdio')"
			fi
			# Check WFx SDIO driver modules existence
			if [ -z "$wfx_core_module" ]; then
				missing_files=$missing_files + 1
				echo "Setup:    Error: Missing WFX core driver   ($wfx_core_link)"
				echo "                 You need to check you WFX driver installation! Make sure you have the $wfx_core_link file!"
			fi
			if [ -z "$wfx_sdio_module" ]; then
				missing_files=$missing_files + 1
				echo "Setup:    Error: Missing WFX SDIO driver   ($wfx_sdio_link)"
				echo "                 You need to check you WFX driver installation! Make sure you have the $wfx_sdio_link file!"
			fi
			# Continue the SDIO checks only if both CORE and SDIO drivers are present
			if [ -n "$wfx_core_module" ]; then
				wfx_core_version=$(modinfo wfx_core  | grep -E "^version")
				echo "Setup:    WFX CORE module $wfx_core_version ($wfx_core_module)"
				if [ -n "$wfx_sdio_module" ]; then
					wfx_sdio_version=$(modinfo wfx_wlan_sdio  | grep -E "^version")
					echo "Setup:    WFX SDIO module $wfx_sdio_version ($wfx_sdio_module)"
				fi
			fi
		else
			echo "Startup:  Error: No part detected at boot on SDIO bus!"
			echo "                 Is there an EVB attached to the Pi, with the bus selection switch set to 'SDIO'?"
			exit 1
		fi
	fi
fi

# SPI test: first of all, check if SPI overlay is enabled in .boot/config.txt
SPI_overlay=$(cat /boot/config.txt | grep ^dtoverlay= | grep wfx-spi)
if [ -z "$SPI_overlay" ]; then
	WFX_SPI_Overlay_enabled=0
else
	WFX_SPI_Overlay_enabled=1
	WFX_DRIVER=wfx_wlan_spi
	echo "User:     WFX SPI overlay_enabled          (in /boot/config.txt)"
	# SDIO detection at boot will only occur if sdio overlay is enabled in boot/config.txt
	if [ "$WFX_SPI_Overlay_enabled" = 1 ]; then
		# Check if SPI driver is blacklisted
		SPI_blacklisted=$(cat /etc/modprobe.d/raspi-blacklist.conf | grep ^blacklist | grep wfx_wlan_spi)
		if [ -z "$SPI_blacklisted" ]; then
			WFX_SPI_Driver_blacklisted=0
			echo "User:     WFX SPI  Driver not blacklisted  (it should load automatically after boot)"
		else
			WFX_SPI_Driver_blacklisted=1
			echo "User:     WFX SPI  Driver blacklisted      (it must be loaded using 'sudo modprobe -v wfx_wlan_spi')"
		fi
		# Check WFx SPI driver modules existence
		if [ -z "$wfx_core_module" ]; then
			missing_files=$missing_files + 1
			echo "Setup:    Error: Missing WFX core driver   ($wfx_core_link)"
			echo "                 You need to check you WFX driver installation! Make sure you have the $wfx_core_link file!"
		fi
		if [ -z "$wfx_spi_module" ]; then
			missing_files=$missing_files + 1
			echo "Setup:    Error: Missing WFX SPI  driver   ($wfx_spi_link)"
			echo "                 You need to check you WFX driver installation! Make sure you have the $wfx_spi_link file!"
		fi
		# Continue the SPI checks only if both CORE and SPI drivers are present
		if [ -n "$wfx_core_module" ]; then
			wfx_core_version=$(modinfo wfx_core  | grep -E "^version")
			echo "Setup:    WFX CORE module $wfx_core_version ($wfx_core_module)"
			if [ -n "$wfx_spi_module" ]; then
				wfx_spi_version=$(modinfo wfx_wlan_spi  | grep -E "^version")
				echo "Setup:    WFX SPI  module $wfx_spi_version ($wfx_spi_module)"
			fi
		fi
	fi
fi

if [ -z "$wfx_fw_file" ]; then
	missing_files=$missing_files + 1
	echo "Setup:    Error: Missing WFX FW file driver ($wfx_fw_file)"
	echo "                 You need to check you WFX driver installation! Make sure you have the $wfx_fw_file file!"
fi
if [ -z "$wfx_pds_file" ]; then
	missing_files=$missing_files + 1
	echo "Setup:    Error: Missing WFX FW file driver ($wfx_pds_file)"
	echo "                 You need to check you WFX driver installation! Make sure you have the $wfx_pds_file file!"
fi

if [ -n "$wfx_fw_file" ]; then
	echo "Setup:    WFX Firmware      $wfx_fw_link ($wfx_fw_base)"
fi
if [ -n "$wfx_pds_file" ]; then
	echo "Setup:    WFX PDS           $wfx_pds_link ($wfx_pds_base)"
fi
if [ -n "$wfx_power_mode_option" ]; then
	echo "User:     WFX Power mode    $wfx_power_mode_option"
fi

if [ $missing_files -gt 0 ]; then
	echo "Setup:   ERROR: There are $missing_files missing files!"
	echo "         Check your installation based on the above recommendations, and try again."
	echo "         It may be worth using 'sudo halt' (to make sure any change is saved), waiting for the activity led to stop blinking then power-cycling the Pi."
	exit 1
else
	# Check if driver has already been loaded
	wfx_loading=$(dmesg | grep wfx)
	if [ -n "$wfx_loading" ]; then
		wfx_startup=$(dmesg | grep wfx | grep "Startup OK")
		if [ -n "$wfx_startup" ]; then
			wfx_driver_success=$(ifconfig wlan0)
			if [ -n "$wfx_driver_success" ]; then
				echo "Startup:  all OK, WFx part ready to act as wlan0"
				echo "Startup:  FW $(dmesg | grep Label.)"
				echo "Startup:  current wlan0 status from 'iwconfig wlan0':"
				echo "$(iwconfig wlan0)"
			else
				echo "Startup:  Error: WFx part not visible as wlan0"
				echo "               dmesg info:\n$(dmesg | grep wfx)"
				echo "               Look at the complete dmesg to get more details"
				echo "               Contact Silicon Labs with a capture of the above information for assistance"
				exit 1
			fi
		else
			echo "Startup:  Error: WFx part driver loading failed"
			echo "               dmesg info:\n$(dmesg | grep wfx)"
			echo "               Look at the complete dmesg to get more details"
			echo "               Contact Silicon Labs with a capture of the above information for assistance"
			exit 1
		fi
	else
		echo "Startup:  Waiting for user to use 'sudo modprobe -v $WFX_DRIVER' to load the driver"
		exit 1
	fi
fi
