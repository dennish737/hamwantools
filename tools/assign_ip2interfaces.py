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
from parsers.dbtools import DbSqlite

description = """
assign_ip2interfaces.py - this script assigns ip addresses to ether, ptp wlan and vrrp interfaces equipment. 
This tool can be used to assign addresses at the organization, site or equipment level. At the at the equipment level,
only the equipment interfaces are added, at the site level, the interfaces of all the equipment are added and finally
at the organizational level (default) all sites and equipment receive IP addresses. This tool currently does not 
allocate ip addresses to sector devices.
Addresses are assigned on a first come first serve basis
"""
# dict <CIDR>:<num_addresses>
block_sizes = {16:65536,17:32768,18:16384, 19:8192, 20:4096, 21:2048, 22:1024, 23:512, 24:256, 25:128, 26:64, 27:32, 28:16}


def main(args):
    dirs = check_dirs(['outputs', 'logs'])
    out_dir = dirs[0]
    log_dir = dirs[1]

    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = os.path.join(log_dir, ('add_ip2interfaces' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.log'))
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))
    # enable sqlite np.int64

    db = DbSqlite()
    db.connect(args.db)

    org_id = db.getOrganizationId(args.club)
    if org_id is None:
        logging.info(f"unable to find org_id for {args.club}")
        exit(1)

    site_id = None
    if args.site:
        site_id = db.getSiteId(org_id, args.site)

    equip_id = None
    if args.equip:
        equip_id = db.getEquipmentId(org_id, args.equip)

    default_gateway_if = False
    ether_if = False
    backbone_if = False
    print("args.assign=", args.assign)
    if args.assign.lower() == 'back':
        backbone_if = True
    elif args.assign.lower() == 'dftgw':
        default_gateway_if = True
    elif args.assign.lower() == 'ether':
        ether_if = True
    else:
        default_gateway_if = True
        ether_if = True
        backbone_if = True

    if default_gateway_if:
        if args.default_ip is None:
            assign_default_gateway_interfaces(db, org_id, site_id, equip_id)
        else:
            assign_default_gw_ip(db, org_id, site_id, equip_id, args.default_ip)

    if ether_if:
        assign_ether_interfaces(db, org_id, site_id, equip_id)

    if backbone_if:
        assign_backbone_interfaces(db,org_id, site_id, equip_id)


def assign_default_gw_ip(db, org_id, site_id, equip_id, default_ip):
    logging.info("User setting gateway default ip to {0}".format(default_ip))
    print("User setting gateway default ip to {0}".format(default_ip))
    print("not implemented")

def assign_default_gateway_interfaces(db, org_id, site_id, equip_id):
    logging.info("starting assign_default_gateway")

    gateways = db.getDefaultGateways(org_id)
    # see if we need to assign an ip address to a default gateway

    for idx, row in gateways.iterrows():
        if row['ip_address'] is None:
            ip_id, ip_addr = db.gerFirstAvailableEtherIpAddress(org_id)
            gateways.iloc[idx]['ip_id'] = ip_id
            gateways.iloc[idx]['ip_address'] = ip_addr
            db.assignEtherIpAddress(row['id'], ip_id)

    # now update all vrrp with the same name
    query = """SELECT  if.id, if.equip_id, ip.id as ip_id,  ip.ip_address
            FROM sites s
            INNER JOIN site_equipment se
            ON se.site_id = s.id
            INNER JOIN interfaces if
            ON if.equip_id = se.id
            LEFT OUTER JOIN ip_addresses ip
            ON ip.id = if.addr_id
            WHERE s.org_id = {0} """.format(org_id)

    if site_id is not None:
        query = query + "AND se_site_id = {0}".format(site_id)

    if equip_id is not None:
        query = query + "AND equip_id = {0}".format(site_id)

    for idx, row in gateways.iterrows():
        ip_addr_id = row['ip_id']
        if_name = row['if_name']
        vrrp_ifs = db.getQueryData(query +  " AND lower(if.if_name) = '{0}';".format( if_name))
        for v_idx, vrrp in vrrp_ifs.iterrows():
            if vrrp['ip_address'] is None:
                db.linkEtherIpAddress(vrrp['id'], ip_addr_id)

def assign_ether_interfaces(db, org_id, site_id, equip_id):
    logging.info("starting assign_ether_interfaces")
    query = """SELECT  if.id, if.equip_id, if.if_type, if.if_name, ip.id as ip_id,  ip.ip_address
            FROM sites s
            INNER JOIN site_equipment se
            ON se.site_id = s.id
            INNER JOIN interfaces if
            ON if.equip_id = se.id
            LEFT OUTER JOIN ip_addresses ip
            ON ip.id = if.addr_id
            WHERE s.org_id = {0} """.format(org_id)

    if site_id is not None:
        query = query + "AND se_site_id = {0}".format(site_id)

    if equip_id is not None:
        query = query + "AND equip_id = {0}".format(site_id)

    ether_ifs = db.getQueryData(query + " AND lower(if.if_type) = 'ether';")

    # loop through the interfaces and assign ip addresses to all ether interfaces
    for idx, ether in ether_ifs.iterrows():
        if ether['ip_address'] is None:
            ip_id, ip_addr = db.gerFirstAvailableEtherIpAddress(org_id)
            #ether_ifs.iloc[idx]['ip_id'] = ip_id
            #ether_ifs.iloc[idx]['ip_address'] = ip_addr
            db.assignEtherIpAddress(ether['id'], ip_id)



def assign_backbone_interfaces(db,org_id, site_id, equip_id):
    logging.info("starting assign_backbone_interfaces")
    query1 = """SELECT id, org_id, device_a, device_b, ptp_block FROM paths WHERE org_id = {0}
        AND type_id = (SELECT x.id FROM path_types x WHERE lower(description) = '{1}');""".format(org_id, 'backbone')

    ptp_paths = db.getQueryData(query1)
    for idx, ptp_path in ptp_paths.iterrows():
        if ptp_path['ptp_block'] is None:
            path_id = ptp_path['id']
            block = db.getFirstAvailablePTPBlock(org_id)

            db.assignPTPBlockToPath(path_id, block['id'])
            check_ptp_devices(db, ptp_path, block)
        else:
            block = db.getPTPBlock(ptp_path['ptp_block'])
            check_ptp_devices(db, ptp_path, block)

def check_dirs(dir_list):
    global base_dir
    dirs = []
    for dir in dir_list:
        path = os.path.join(base_dir, dir)
        if not os.path.isdir(path):
            os.makedirs(path)
        dirs.append(path)
    return dirs

def check_ptp_devices(db, ptp_path, ptp_block):
    eqp_a_list = db.getEquipmentInfo(ptp_path['device_a'], 'wlan')
    eqp_b_list = db.getEquipmentInfo(ptp_path['device_b'], 'wlan')
    device_a = None
    device_b = None
    # check to see if we have more than one wlan interface
    if len(eqp_a_list) > 1 or len(eqp_b_list) > 1:
        logging.warning("device has more thant one wlan, dev_a = {0}, device_b = {1}, using wlan1".format(
            ptp_path['device_a'], ptp_path['device_b']))

        for i in range(eqp_a_list):
            if 'wlan1' in eqp_a_list[i].keys():
                device_a = eqp_a_list[i]
        for i in range(eqp_b_list):
            if 'wlan1' in eqp_b_list[i].keys():
                device_b = eqp_b_list[i]
    else:
        device_a = eqp_a_list[0]
        device_b = eqp_b_list[0]
    # check and make sure we have an eqp_a and eqp_b block
    if device_a is not None and device_a['ip_address'] is None:

        # update the 'a' interface
        db.assignEtherIpAddress(device_a['if_id'], ptp_block['ip_a'])
    elif device_a is not None:

        logging.warning("device {0} ip_address already assigned, {1}".format(device_a['dev_id'], device_a['ip_address']))
    else:
        logging.warning("No device 'a' specified in path {0}.".formatptp_path['id'])

    if device_b is not None and device_b['ip_address'] is None:
        # update the 'a' interface
        db.assignEtherIpAddress(device_b['if_id'], ptp_block['ip_b'])
    elif device_b is not None:
        logging.warning("device {0} ip_address already assigned, {1}".format(device_b['dev_id'], device_b['ip_address']))
    else:
        logging.warning("No device 'b' specified in path {0}.".formatptp_path['id'])





if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--club', help='club name',required=True)
    parser.add_argument('-s', '--site',  help='Site Name', default=None)
    parser.add_argument('-e', '--equip', help='Equipment Name', default=None)
    parser.add_argument('--dftgw', help='Assign addresses to the default gateway vrrp interfaces', action='store_true')
    parser.add_argument('--ether', help='Assign addresses to ether interfaces', action='store_true')
    parser.add_argument('--back', help='Assign Addresses to backbone interfaces', action='store_true')
    parser.add_argument('--default_ip', help='IP address to use for default ip', default=None)
    parser.add_argument('--assign', default='all', const='all',
                        nargs='?',
                        choices=["all", "dftgw", "ether", "ptp"],
                        help='Assign ip addresses to: all | dftgw (default gateway) | ether | ptp  (default: %(default)s')
    parser.add_argument('--db', help='configuration db', required=True)
    parser.add_argument('-l', '--log', default=None, help='logging file, default will be system name')

    if TEST == True:
        in_args = ['-c', 'example_club','--db', '../data/planning_example.sqlite3']
        #in_args = ['-c', 'spokane', '--db', '../data/planning_spokane.sqlite3']
        args = parser.parse_args(in_args)
    else:
        args = parser.parse_args()


    main(args)