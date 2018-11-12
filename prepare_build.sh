#!/bin/bash
set -ex

# Use `uname -r` to retrieve your current kernel version.
KERNEL_VERSION=$(uname -r)

## Create a new build directory and cd in this directory
mkdir -p ${HOME}/build
cd ${HOME}/build
BUILD_DIR=$(pwd)

## Retrieve your original firmware git hash
FIRMWARE_GIT_HASH=$(zgrep "* firmware as of"  /usr/share/doc/raspberrypi-bootloader/changelog.Debian.gz | head -1 | awk '{print $5}' )

## Retrieve your original table of kernel symbols
wget https://raw.github.com/raspberrypi/firmware/$FIRMWARE_GIT_HASH/extra/Module7.symvers
mv Module7.symvers  Module.symvers

## Retrieve your linux git hash (for the kernel source code)
wget https://raw.github.com/raspberrypi/firmware/$FIRMWARE_GIT_HASH/extra/git_hash
LINUX_GIT_HASH=$(cat git_hash)

## Download the linux source code for your 'linux git hash', then delete the zip file to save disk space.
sudo wget https://github.com/raspberrypi/linux/archive/$LINUX_GIT_HASH.zip
unzip $LINUX_GIT_HASH.zip
mv linux-$LINUX_GIT_HASH/* $BUILD_DIR
rm --recursive --force linux-$LINUX_GIT_HASH
rm $LINUX_GIT_HASH.zip

## Retrieve the original Pi kernel configuration file
sudo modprobe configs
gunzip --keep --stdout /proc/config.gz > $BUILD_DIR/arch/arm/configs/my_defconfig

## Configure the build chain
sudo  ln --symbolic  $BUILD_DIR    /lib/modules/$KERNEL_VERSION/build

## Install 'bc' if not already installed
sudo apt-get install bc

# Set the kernel release for modules_install
cd $BUILD_DIR
sed -i 's/CONFIG_LOCALVERSION="-v7"/CONFIG_LOCALVERSION="-v7+"/' arch/arm/configs/my_defconfig

## Configure modules compilation
cd $BUILD_DIR
make my_defconfig

## Prepare for modules compilation
cd $BUILD_DIR
make modules_prepare

### Check:
cd $BUILD_DIR
cat  include/config/kernel.release

### Check compilation of an already existing module
cd $BUILD_DIR
make SUBDIRS=$BUILD_DIR/drivers/i2c/algos/
# This should compile without errors, and the resulting .ko file should be created under $BUILD_DIR/drivers/i2c/algos within seconds.
ls $BUILD_DIR/drivers/i2c/algos/*.ko
