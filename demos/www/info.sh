#!/bin/bash
# Copyright (c) 2018, Silicon Laboratories
# See license terms contained in COPYING file

. wfx_set_env

case "${1}" in
    ap)
        if [ ! -z ${2} ]; then
            conf_res=$(cat ${GITHUB_CONF_PATH}/hostapd.conf | grep ${2})
            if [ "${conf_res}" != "" ]; then
                printf "${conf_res}"
            else
                conf_res=$(hostapd_cli status | grep ${2})
                if [ "${conf_res}" != "" ]; then
                    printf "${conf_res}"
                fi
            fi
        else
            echo "usage: sudo wfx_info ap [ssid|country_code|channel|auth_algs|ieee80211n|wpa|wpa_key_mgmt|rsn_pairwise|wpa_passphrase] "
        fi
        ;;
    sta|station)
        if [ ! -z ${2} ]; then
            case "${2}" in
                scan)
                    wpa_cli scan > /dev/null
                    scan_res="$(wpa_cli scan_results)"
                    echo  "${scan_res}" | grep ":"
                    ;;
                *)
                    conf_res=$(cat ${GITHUB_CONF_PATH}/wpa_supplicant.conf | grep ${2})
                    if [ "${conf_res}" != "" ]; then
                        printf "${conf_res}"
                    else
                        conf_res="$(wpa_cli status | grep ${2})"
                        if [ "${conf_res}" != "" ]; then
                            printf "${conf_res}"
                        fi
                    fi
                    ;;
            esac
        else
            echo "usage: sudo wfx_info station [scan|ctrl_interface|GROUP|update_config|country] "
        fi
        ;;
    dnsmasq)
        if [ ! -z ${2} ]; then
            printf "$(cat ${GITHUB_CONF_PATH}/dnsmasq.conf | grep ${2})"
        else
            echo "usage: sudo wfx_info dnsmasq [interface|dhcp-range|addn-hosts|domain] "
        fi
        ;;
    ip)
        case "${2}" in
            eth)
                printf "$(ip addr show | grep "global eth" | grep 'inet '| cut -d '/' -f 1 | cut -d ' ' -f 6)"
                ;;
            wlan)
                printf "$(ip addr show | grep "global wlan" | grep 'inet '| cut -d '/' -f 1 | cut -d ' ' -f 6)"
                ;;
            *)
                echo "usage: sudo wfx_info ip [eth|wlan]"
                ;;
        esac
        ;;
    mac)
        case "${2}" in
            eth)
                printf "$(ip addr show eth0  | grep 'link/ether' | cut -d ' ' -f 6)"
                ;;
            wlan)
                printf "$(ip addr show wlan0 | grep 'link/ether' | cut -d ' ' -f 6)"
                ;;
            *)
                echo "usage: sudo wfx_info mac [eth|wlan]"
                ;;
        esac
        ;;
    *)
        if [ -z ${1} ]; then
            echo "usage: sudo wfx_info [ap|station|dnsmasq|ip|mac] [args]"
        fi
        echo $($@)
        exit 1
        ;;
esac
