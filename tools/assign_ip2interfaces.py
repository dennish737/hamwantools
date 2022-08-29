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
assign_ip2interfaces.py - this script assigns ip addresses to interfaces like, ether, ptp wlan and vrrp . 
This tool can be used to assign addresses at the organization, site or equipment level. At the at the equipment level,
only the equipment interfaces are added, at the site level, the interfaces of all the equipment are added and finally
at the organizational level (default) all sites and equipment receive IP addresses. This tool currently does not 
allocate ip addresses to sector devices.
Addresses are assigned on a first come first serve basis
"""
# dict <CIDR>:<num_addresses>
block_sizes = {16:65536,17:32768,18:16384, 19:8192, 20:4096, 21:2048, 22:1024, 23:512, 24:256, 25:128, 26:64, 27:32, 28:16}

#-----------------------------------------------------------------------------------------
# This is where the magic begins. Up to now we have built a logical network, now we need to connect things together so we
# can move packets between equipment and sites.
# Starting with a Site, we need to first connect all the equipment. To do this we must assign IP addresses to the ether
# interfaces, and connect them to the switch. We start by getting the reserved address block reserved for the site router
# R1.<site> and assign it to R1, and assign the ether1 interface to the first available ip address in the pool. We then assign
# ip addresses from the pool to the remaining equipment 'ether1' interfaces on the site (e.g. s1,s2,s3, ptp1, ...)
# once that is done, we assign the remaining ip address in the pool to the DHCP pool for R1
# Next we move to assigning addresses to the sector wlan ports. We do this by assigning the first reserved pool for each
# sector devices, and use the first ip address of the pool to the wlan1 interface, and the remaining addresses to the
# dhcp pool for the sector.

def main(args):
    dirs = check_dirs(['outputs', 'logs'])
    out_dir = dirs[0]
    log_dir = dirs[1]

    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = os.path.join(log_dir, ('assign_ip2interfaces' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.log'))
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

    site_ids = None
    if args.sites:
        logging.info("getting ids for sites: {0}".format(args.sites))
        site_ids = []
        #get ids for each site
        for site in args.sites:
            site_ids.append(db.getSiteId(org_id, site))
    else:
        logging.info("getting all sites")
        #get all sites
        site_ids = db.getListOfAllSiteIds(org_id)

    path_ids = None
    if args.paths:
        logging.info("getting ids for paths: {0}".format(args.paths))
        path_ids = []
        for path_name in args.paths:
            path_ids.append(db.getPathId(org_id, path_name, 'backbone'))
    else:
        path_ids = db.getListOfPathIds(org_id, 'backbone')

    groups = db.getEquipmentGroups()
    logging.info("processing addresses for sites = [ {0} ]".format(args.sites))

    vrrp_if = False
    router_if = False
    backbone_if = False
    sector_if = False

    if args.assign.lower() == 'back':
        backbone_if = True
    elif args.assign.lower() == 'vrrp':
        vrrp_if = True
    elif args.assign.lower() == 'router':
        router_if = True
    elif args.assign.lower() == 'sector':
        sector_if = True
    else:
        vrrp_if = True
        router_if = False
        backbone_if = False
        sector_if = False


    #if default_gateway_if:
    #    assign_default_gateway_interfaces(db, org_id, site_ids)

    #if router_if:
    #    assign_router_interfaces(db, org_id, site_ids, groups)

    #if backbone_if:
    #    assign_backbone_interfaces(db,org_id, path_ids)

    #if sector_if:
    #    assign_sector_interfaces(db,org_id,site_ids, groups)

    if vrrp_if:
        assign_vrrp_interfaces(db,org_id, site_ids)



def assign_ospf_interfaces(db, org_id, site_ids):
    logging.info("starting assign_ether_ip")
    # for site_id in site_id:
    #

def assign_vrrp_interfaces(db, org_id, site_ids):
    logging.info("starting assign_default_gateway")
    # we have assigned vrrp interfaces to all equipment.
    # for now only sector vrrp interfaces are used.
    # the vrrp ip address is the broadcast address of the
    # ip block assigned to the wlan interface
    query = """SELECT  if.id, if.equip_id, if.if_type, if.if_name, ip.id as ip_id,  ip.ip_address
            FROM sites s
            INNER JOIN site_equipment se
            ON se.site_id = s.id
            INNER JOIN interfaces if
            ON if.equip_id = se.id
            LEFT OUTER JOIN ip_addresses ip
            ON ip.id = if.addr_id
            WHERE s.org_id = ? AND se.site_id = ? 
			AND se.group_id = (SELECT eqg.id FROM equipment_groups eqg WHERE eqg.group_name = 'sector')
			AND lower(if.if_type) = 'vrrp' 
            ORDER BY s.id, se.id, if.id;
    """
    # loop through sites and assign dhcp blocks to equipment
    for site_id in site_ids:
        # get dhcp interfaces for equipment
        vrrp_ifs = db.getQueryData(query,org_id, site_id)
        if vrrp_ifs is not None:
            for idx, vrrp_if in vrrp_ifs.iterrows():
                if vrrp_if['ip_address'] is None:
                    equip_id = vrrp_if['equip_id']
                    vrrp_addresses = db.getSiteDeviceVRRPAddresses(org_id, equip_id)
                    if len(vrrp_addresses) > 0:
                        if_id = vrrp_if['id']
                        ip_id = vrrp_addresses[0]['vrrp_addr_id']
                        db.assignInterfaceIPAddress(if_id, ip_id)


def assign_dhcp_interfaces(db, org_id, site_ids):
    logging.info("starting assign_dhcp_interfaces")
    query = """SELECT  if.id, if.equip_id, if.if_type, if.if_name, ip.id as ip_id,  ip.ip_address
            FROM sites s
            INNER JOIN site_equipment se
            ON se.site_id = s.id
            INNER JOIN interfaces if
            ON if.equip_id = se.id
            LEFT OUTER JOIN ip_addresses ip
            ON ip.id = if.addr_id
            WHERE s.org_id = ? AND se.site_id = ? AND lower(if.if_type) = 'dhcp' 
            ORDER BY s.id, se.id, if.id;"""

    # loop through sites and assign dhcp blocks to equipment
    for site_id in site_ids:
        # get dhcp interfaces for equipment
        dhcp_ifs = db.getQueryData(query,org_id, site_id)

        if dhcp_ifs is not None:
            for idx, dhcp_if in dhcp_ifs.iterrows():
                if dhcp_if['ip_address'] is None:
                    # block is a dictionary, with id network, start_ip, end_ip and broadcast
                    block = db.getFirstAvailableAddressBlock(org_id)
                    if block is not None:
                        db.assignAddressBlock(dhcp_if['id'], block['id'])


# assign_router_interfaces
# for each site, assign the address block to the R1 device
# then for each ether1 interface, assign ip from pool
# at the end add the remaining ip addresses to the dhcp pool
def assign_router_interfaces(db, org_id, site_ids, groups):
    logging.info("starting assign_router_interfaces")
    for site_id in site_ids:
        logging.info("starting site {0}".format(site_id))
        # get address block for site router (one per router)
        # returned as a list of dictionaries
        blocks = db.getSiteRouterAddressBlock(site_id)
        block = None
        # note current design has one site router per site. Future designs
        # may have more than one. In that case we will have multiple blocks returned,
        # one per router, and we should 'loop' through the routers
        gateway_id = None
        if blocks:
            block = blocks[0]
            df_equipment = db.getSiteEquipmentById(site_id)
            if df_equipment is None:
                logging.warning("Site {0} has no equipment. Skipping")
                continue
            # normally the router is the first device, but just in case we will
            # loop through and find the router and configure it
            # then we will loop through again, and set the other devices
            # the site router we want to configure is the one that reserved
            # the address block
            for idx, device in df_equipment.iterrows():
                if device['id'] == block['reserved']:
                    # we have site router
                    dev_id = device['id']
                    block_id = block['id']
                    logging.info("configuring site router {0}, {1}, address block {2}".format(dev_id, device['device_name'], block_id))
                    params = db.getEquipmentInterfaces(dev_id, 'ether')[0]
                    if_id = params['id']
                    if params['addr_id'] is None:
                        ip_id, ip_addr = db.getFirstAvailableIPFromBlock(block_id)
                        gateway_id = ip_id
                        db.assignAddressBlock(dev_id, block_id)
                        db.assignInterfaceIPAddress(if_id, ip_id)
                        logging.info("assigning ip {0},{1} to interface {2}".format(ip_id, ip_addr, if_id))
                    else:
                        logging.warning("interface {0} already assigned ip_address {1}, skipping".format(if_id, params['addr_id']))
                        gateway_id = params['addr_id']
                    break
            for idx, device in df_equipment.iterrows():
                if device['id'] != block['reserved']:
                    # We have a sector or ptp device
                    group_name = list(groups.keys())[list(groups.values()).index(device['group_id'])]
                    dev_id = device['id']
                    block_id = block['id']
                    logging.info("configuring site device {0}, {1}, address block {2}".format(dev_id, device['device_name'],
                                 block_id))
                    params = db.getEquipmentInterfaces(dev_id, 'ether')[0]
                    if_id = params['id']
                    if params['addr_id'] is None:
                        ip_id, ip_addr = db.getFirstAvailableIPFromBlock(block_id)
                        db.assignInterfaceIPAddress(if_id, ip_id)
                        logging.info("assigning ip {0},{1} to interface {2}".format(ip_id, ip_addr, if_id))
                    else:
                        logging.warning("interface {0} already assigned ip_address {1}, skipping".format(if_id, params['addr_id']))

            # assign remaining addresses to DHCP device
            dev_id = block['reserved']
            dev_name = df_equipment.loc[df_equipment['id'] == dev_id, 'device_name'].item()
            params = db.getEquipmentInterfaces(dev_id, 'dhcp')[0]
            # if the device does not have a dhcp  interface, params will be None
            if params:
                if params['dhcp_id'] is None:
                    if_id = params['id']
                    pool_name = dev_name + "." + params['if_name']
                    lower_id, lower_addr = db.getFirstAvailableIPFromBlock(block_id)
                    upper_id, upper_addr = db.getLastAvailableIPFromBlock(block_id)
                    network, network_addr = db.getNetworkIPFromBlock(block_id)

                    dhcp_id = db.createDHCPBlock(org_id, if_id, pool_name, network, lower_id, upper_id, gateway_id, None)
                    #
                    logging.info("dhcp pool {0},{1} created for device {2}, {3}".format(pool_name, dhcp_id, dev_id, if_id))
                else:
                    logging.warning("dhcp interface {0}, already assigned {1}".format(if_id, params['dhcp_id']))
            else:
                logging.error("interface {0}, {1} has no dhcp interface.".format(device['device_name'], dev_id))

def assign_backbone_interfaces(db,org_id, path_ids):
    # The back boone devices connect the sites with paths
    logging.info("starting assign_backbone_interfaces")
    query1 = """SELECT id, org_id, device_a, device_b, ptp_block FROM paths WHERE org_id = ?
        AND type_id = (SELECT x.id FROM path_types x WHERE lower(description) = ?);"""

    # assign ip addresses to all paths, skip if already assigned
    ptp_paths = db.getQueryData(query1, org_id, 'backbone')
    for idx, ptp_path in ptp_paths.iterrows():
        if np.isnan(ptp_path['ptp_block']) :
            path_id = ptp_path['id']
            block = db.getFirstAvailablePTPBlock(org_id)
            if block:
                db.assignPTPBlockToPath(path_id, block['id'])
                check_ptp_devices(db, ptp_path, block)
            else:
                logging.error("no ptp blocks available for org_id = {0}".format(org_id))
                raise ValueError("out of ptp blocks")
        else:
            logging.warning("block {0} all reading assigned to path {1}.".format(ptp_path['ptp_block'],ptp_path['id']))
            block = db.getPTPBlock(ptp_path['ptp_block'])
            check_ptp_devices(db, ptp_path, block)

def assign_sector_interfaces(db, org_id, site_ids, groups):
    logging.info("starting assign_sector_interfaces")
    for site_id in site_ids:
        logging.info("starting site {0}".format(site_id))
        # get sector devices
        device_type = groups['sector']

        df_equipment = db.getSiteEquipmentByIdAndType(site_id, device_type)

        if df_equipment is None:
            logging.warning("Site {0} has no equipment. Skipping")
            continue


        for idx, device in df_equipment.iterrows():
            dev_id = device['id']
            blocks = db.getSiteDeviceAddressBlock(dev_id)
            block = None

            if blocks and len(blocks) > 0:
                block = blocks[0]
                block_id = block['id']
                logging.info("configuring sector router {0}, {1}, address block {2}".format(dev_id, device['device_name'],
                                                                                          block_id))
                params = db.getEquipmentInterfaces(dev_id, 'wlan')[0]

                if params is None:
                    continue
                if_id = params['id']

                if params['addr_id'] is None:
                    ip_id, ip_addr = db.getFirstAvailableIPFromBlock(block_id)
                    gateway_id = ip_id
                    db.assignAddressBlock(dev_id, block_id)
                    db.assignInterfaceIPAddress(if_id, ip_id)
                    logging.info("assigning ip {0},{1} to interface {2}".format(ip_id, ip_addr, if_id))
                else:
                    logging.warning(
                        "interface {0} already assigned ip_address {1}, skipping".format(if_id, params['addr_id']))
                    gateway_id = params['addr_id']

                # assign remaining addresses to DHCP device
                params = db.getEquipmentInterfaces(dev_id, 'dhcp')[0]
                # if the device does not have a dhcp  interface, params will be None
                if params:
                    if params['dhcp_id'] is None:
                        if_id = params['id']
                        pool_name = device['device_name'] + "." + params['if_name']
                        lower_id, lower_addr = db.getFirstAvailableIPFromBlock(block_id)
                        upper_id, upper_addr = db.getLastAvailableIPFromBlock(block_id)
                        network, network_addr = db.getNetworkIPFromBlock(block_id)

                        dhcp_id = db.createDHCPBlock(org_id, if_id, pool_name, network, lower_id, upper_id, gateway_id,
                                                     None)
                        #
                        logging.info(
                            "dhcp pool {0},{1} created for device {2}, {3}".format(pool_name, dhcp_id, dev_id, if_id))
                    else:
                        logging.warning("dhcp interface {0}, alread assigned {1}".format(if_id, params['dhcp_id']))
                else:
                    logging.error("interface {0}, {1} has no dhcp interface.".format(device['device_name'], dev_id))


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

def check_ptp_devices(db, ptp_path, ptp_block):
    eqp_a_list = db._getEquipmentInfo(ptp_path['device_a'])
    eqp_b_list = db._getEquipmentInfo(ptp_path['device_b'])
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
        db.assignInterfaceIPAddress(device_a['if_id'], ptp_block['ip_a'])
    elif device_a is not None:
        logging.warning("device {0} ip_address already assigned, {1}".format(device_a['dev_id'], device_a['ip_address']))
    else:
        logging.warning("No device 'a' specified in path {0}.".formatptp_path['id'])

    if device_b is not None and device_b['ip_address'] is None:
        # update the 'b' interface
        db.assignInterfaceIPAddress(device_b['if_id'], ptp_block['ip_b'])
    elif device_b is not None:
        logging.warning("device {0} ip_address already assigned, {1}".format(device_b['dev_id'], device_b['ip_address']))
    else:
        logging.warning("No device 'b' specified in path {0}.".formatptp_path['id'])




if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--club', help='club name',required=True)
    parser.add_argument('-e', '--equip', help='Equipment Name', default=None)

    parser.add_argument('--assign', default='all', const='all',
                        nargs='?',
                        choices=["all", "router", "sector", "bptp", "vrrp", "dhcp", "ospf"],
                        help='Assign ip addresses to: all | dftgw (default gateway) | ether | ptp  (default: %(default)s')

    parser.add_argument('--db', help='configuration db', required=True)
    parser.add_argument('-l', '--log', default=None, help='logging file, default will be system name')
    parser.add_argument('--log_level', default='warning', const='warning',
                        nargs='?',
                        choices=["debug", "info", "warning", "error", "critical"],
                        help='assign loging level')
    parser.add_argument('--sites', nargs='*', help='A list of sites to add ip addresses to. If none are provided, all sites will receive ip addresses')
    parser.add_argument('--paths', nargs='*',
                        help='A list of paths to add ip addresses to. If none are provided, all sites will receive ip addresses')

    if TEST == True:
        in_args = ['-c', 'example_club','--db', '../data/planning_example.sqlite3']
        #in_args = ['-c', 'spokane', '--db', '../data/spokane_example.sqlite3']
        args = parser.parse_args(in_args)
    else:
        args = parser.parse_args()


    main(args)
    #print(args)