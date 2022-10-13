import argparse

from argparse import ArgumentParser

import os
import sys
import datetime
import sqlite3

from datetime import datetime
import pandas as pd
import numpy as np
import ipaddress

import logging

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
from libs.dbtools import DbSqlite
from libs.ip_tools import ip2long, ip2hex, int2ip, hex2ip

description = """
Basic_Parser - used to create a config file from database parameters and a template text file"""

dhcp_dict = {
    'DP_DHCP_POOL': 'pool_name',
    'DP_DHCP_NETWORK': 'network',
    'DP_DHCP_LOWER_ADDR': 'lower_addr',
    'DP_DHCP_UPPER_ADDR': 'upper_addr',
    'DP_DHCP_GATEWAY_ADDR': 'gateway_addr',
    'DP_DHCP_DNS_ADDR': 'dns_addr',
}
map_dict = {'DP_ETHER1_IP': 'ether1_ip',
    'DP_DHCP': 'dhcp',
    'DP_NETWORK_ADDRESS': 'network_address',
    'DP_OSPF_NETWORK_ADDRESS': 'ospf_network_address',
    'DP_OSPF_ROUTER_ID': 'ospf_router_id',
    'DP_RADIO_NAME': 'radio_name',
    'DP_REMOTE_IP': 'remote_ip',
    'DP_REMOTE_ROUTER_NAME': 'remote_router_name',
    'DP_ROUTER_NAME': 'router_name',
    'DP_ROUTER_SSID': 'ptp_router_ssid',
    'DP_ROUTER_SSID_KEY': 'ptp_router_key',
    'DP_SYS_NAME': 'sys_name',
    'DP_VRRP1_IP': 'vrrp1_ip',
    'DP_WLAN1_IP': 'wlan1_ip',
    'GP_CLUB_CONTACT': 'club_contact',
    'GP_DNS1_IP': 'dns1',
    'GP_DNS2_IP': 'dns2',
    'GP_LOGGING1_IP': 'logging1_ip',
    'GP_LOGGING2_IP': 'logging2_ip',
    'GP_NTP1_IP': 'ntp1_ip',
    'GP_NTP2_IP': 'ntp2_ip',
    'GP_TIMEZONE': 'timezone',
    'SP_OSPF_KEY': 'ospf_key',
    'SP_CLIENT_PASSWORD': 'client_password',
    'SP_CLIENT_SSID': 'client_ssid',
    'SP_VRRP_KEY': 'vrrp_key',
    'TP_ETHER1': 'ether1_interface',
    'TP_ETHER2': 'ether2_interface',
    'TP_ETHER3': 'ether3_interface',
    'TP_ETHER4': 'ether4_interface',
    'TP_ETHER5': 'ether5_interface',
    'TP_ETHER6': 'ether6_interface',
    'TP_ETHER7': 'ether7_interface',
    'TP_ETHER8': 'ether8_interface',
    'TP_WLAN1': 'wlan1_interface',
    'TP_WLAN2': 'wlan2_interface',
    'TP_VRRP1': 'vrrp1_interface'
}

def main(args):
    dirs = check_dirs(['outputs', 'logs'])
    out_dir = dirs[0]
    log_dir = dirs[1]
    print(args)

    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = os.path.join(log_dir, ('basic_parser' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.log'))
    print(log_file)

    level = get_log_level(args.log_level)
    level = logging.DEBUG
    logging.basicConfig(filename=log_file, encoding='utf-8', level=level)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))

    db = DbSqlite()
    db.connect(args.db)

    org_id = db.getOrganizationId(args.club)
    if org_id is None:
        logging.info(f"unable to find org_id for {args.club}")
        exit(1)
    call_sign = db.getOrganizationCallSign(org_id)
    if call_sign:
        call_sign += '/'
    print("call sign = ", call_sign)

    site_ids = None
    if args.site:
        logging.info("getting ids for site: {0}".format(args.site))
        site_ids = []
        #get ids for each site
        site_ids.append(db.getSiteId(org_id, args.site))
    else:
        logging.info(f"no site specified for  {args.club}")
        exit(1)
    print('Site Name:', args.site.lower())
    print('site_ids =', site_ids)
    print('Device name:', args.device.lower())
    device_id = db.getEquipmentId(org_id, args.device)[0]
    print('Device id:', device_id)
    #print("parameters -------------")
    params = db.getDeviceParameters(device_id, call_sign)
    map_params = {}
    for k,v in map_dict.items():
        if v in params:
            if v == 'dhcp':
                dhcp_params(params[v], map_params)
            else:
                map_params[k] = params[v]
    #print(map_params)
    #print(map_dict)
    #print(params)
    print('        Tag                   Param                ')
    print('---------------------------------------------------')
    for k,v in map_params.items():
        print('{0: <25} {1}'.format(k, v))



def check_dirs(dir_list):
    global base_dir
    dirs = []
    for dir in dir_list:
        path = os.path.join(base_dir, dir)
        if not os.path.isdir(path):
            os.makedirs(path)
        dirs.append(path)
    return dirs

def get_log_level(level):
    log_level = logging.WARNING
    if level == 'debug':
        log_level = logging.DEBUG
    elif level == 'info':
        log_level = logging.INFO
    elif level == 'error':
        log_level = logging.ERROR
    elif level == 'critical':
        log_level = logging.CRITICAL
    else:
        log_level = logging.WARNING
    return log_level

def dhcp_params(params, param_dict):
    # process dhcp info
    for param_set in params:
        for k,v in dhcp_dict.items():
            #print(k,v)
            if v in param_set:
                param_dict[k] = param_set[v]
    return

def site_router():
    pass

def sector_router():
    pass

def ptp_router():
    pass


if __name__ == '__main__':

    TEST = True
    args = None
    parser: ArgumentParser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--club', help='club name', required=True)
    parser.add_argument('--site', help='the name of the site ', required=True)
    parser.add_argument('--device', help='device_name', required=True)
    parser.add_argument('--db', help='configuration db', required=True)

    parser.add_argument('templates', nargs='+', help='a list of templates, at least one required' )

    parser.add_argument('--configs', default='router', const='router',
                        nargs='?',
                        choices=["router", "sector", "bptp", "gateway", 'default_gateway', 'client'],
                        help='Create config files for:[ router | sector | bptp | gateway | default_gateway | client ] (default: %(default)s')


    parser.add_argument('-l', '--log', default=None, help='logging file, default will be system name')
    parser.add_argument('--log_level', default='warning', const='warning',
                        nargs='?',
                        choices=["debug", "info", "warning", "error", "critical"],
                        help='assign loging level')

    if TEST == True:
        #in_args = ['-c', 'example_club','--db', '../data/planning_example.sqlite3']
        in_args = ['-c', 'spokane', '--db', '../data/spokane_example.sqlite3', '--device', 'r1.KRELL', '--site', 'krell', '--configs', 'router',
                   '../templates/r_router_template.txt']
        args = parser.parse_args(in_args)
    else:
        args = parser.parse_args()

    # check and make sure we have the correct number of templates

    main(args)
    #print(args)