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

"""
python script to divide an ip address allocation into blocks
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
        log_file = os.path.join(log_dir, ('add_ipaddresses' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.log'))
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))
    # enable sqlite np.int64

    db = DbSqlite()
    db.connect(args.db)
    org_id = args.club_id
    if org_id is None:
        # use the club name to get the org_id
        org_id = db.getOrganizationId(args.club)
    if org_id is None:
        logging.info(f"unable to find org_id for {args.club}")
        exit(1)

    # get the organization parameters
    organization_params = db.getOrganizationData(org_id)
    block_size = organization_params['block_size']
    ptp_size = organization_params['ptp_net_size']
    device_net_size = organization_params['device_net_size']
    block_size_mask = list(block_sizes.keys())[list(block_sizes.values()).index(block_size)]

    # get all allocations for club
    df = get_unblocked_network_allocations(org_id, db)
    if len(df) < 1:
        logging.info("no network allocation available, exiting")
        print("No network allocation available, exiting ")
        exit(0)
    logging.info("allocations = " + df.to_string().replace('\n', '\n\t'))


    device_offset = device_net_size
    ptp_offset = (ptp_size + device_offset)

    ip_types = db.getIPTypes()
    for i, row in df.iterrows():
        allocation_id = row['id']

        addresses = generate_ip(row)
        records = []

        ptp_index = len(addresses) - ptp_offset -1
        dev_index = len(addresses) - device_offset -1
        for i in range(len(addresses)):
            ip_type = ip_types['pool']
            if i > ptp_index:
                ip_type = ip_types['ptp']
            if i > dev_index:
                ip_type = ip_types['device']
            records.append((org_id, addresses[i],
                            ip_type))
        save_addresses(db, records)
        # add CIDR /31 to ptp addresses
        update_ptp_addresses(db)
        update_device_addresses(db)
        update_pool_addresses(db)

    # create address pools (blocks)
    # get the address to pool
    ip_addresses = db.getPoolAddresses( org_id)
    address_blocks = generate_pool_blocks(ip_addresses, org_id, organization_params['block_size'])

    save_address_blocks(db,address_blocks)

    # reserve the address block ip addresses, and update linkage
    blocks = db.getNewAddressBlocks(org_id)
    update_block_ip(db, blocks)

    # add ptp_blocks
    # Point to Point (ptp) connections require two ip addresses one on each end of the connection.
    # we want addresses blocks to be IP addresses paired by unit distance (e.g. 0-1, 2-3, ...)
    # we have already entered and marked the ip addresses, and marked them for ptp use, we simply need to pair them
    available_ptp_addresses = db.getAvailablePTPIps(org_id)
    logging.debug('available ip_addresses - {}'.format(available_ptp_addresses.to_string()))
    logging.debug('number of available addresses = {}'.format(len(available_ptp_addresses)))

    ptp_blocks = get_ptp_blocks(org_id, available_ptp_addresses)

    save_ptp_blocks(db, ptp_blocks)

    ptp_blocks = db.getNewPTPBlocks(org_id)
    update_ptp_ips(db,ptp_blocks)

    db.close()

def check_dirs(dir_list):
    global base_dir
    dirs = []
    for dir in dir_list:
        path = os.path.join(base_dir, dir)
        if not os.path.isdir(path):
            os.makedirs(path)
        dirs.append(path)
    return dirs

def get_unblocked_network_allocations( id, db):
    query = 'select * from network_allocations where blocks_created = 0 and org_id = {}'
    df = pd.read_sql(query.format(id), db.conn)
    return df

def generate_ip(row):
    ip_start = int(ipaddress.ip_address(row['starting_address']))
    ip_end = int(ipaddress.ip_address(row['ending_address'])) + 1
    addresses = []
    for i in range(ip_start, ip_end):
        addresses.append(str(ipaddress.ip_address(i)))
    return addresses

def get_number_of_addresses(start, end):
    ip_start = int(ipaddress.ip_address(start))
    ip_end = int(ipaddress.ip_address(end))
    num_addresses = ip_end - ip_start + 1
    return num_addresses


def save_addresses(db, records):
    query = 'INSERT INTO ip_addresses (org_id, ip_address, ip_type) VALUES(?,?,?);'
    cursor = db.conn.cursor()
    cursor.executemany(query,records)
    db.conn.commit()

def update_ptp_addresses(db):
    query1 = 'UPDATE ip_addresses set ip_address = ip_address || "/32" where new = 1 AND ip_type = (select id from ip_types where type_name = "ptp");'
    cursor = db.conn.cursor()
    cursor.execute(query1)
    query2 = 'UPDATE ip_addresses set new = 0 where new = 1 AND ip_type = (select id from ip_types where type_name = "ptp");'
    cursor.execute(query2)
    db.conn.commit()

def update_device_addresses(db):
    query1 = 'UPDATE ip_addresses set ip_address = ip_address || "/32" where new = 1 AND ip_type = (select id from ip_types where type_name = "device");'
    cursor = db.conn.cursor()
    cursor.execute(query1)
    query2 = 'UPDATE ip_addresses set new = 0 where new = 1 AND ip_type = (select id from ip_types where type_name = "device");'
    cursor.execute(query2)
    db.conn.commit()

def update_pool_addresses(db):
    query = 'UPDATE ip_addresses set new = 0 where new = 1 AND ip_type = (select id from ip_types where type_name = "pool");'
    cursor = db.conn.cursor()
    cursor.execute(query)
    db.conn.commit()

def generate_pool_blocks( pool_addresses, org_id,block_size):
    # we are going to create block in increments of 16 address
    # the addresses must be continuous but available address space may
    # not be so check.
    start_index = 0
    records = []
    while start_index < len(pool_addresses):
        end_index = get_pool(pool_addresses, start_index, block_size)
        network = pool_addresses.iloc[start_index]['id']
        start_ip = pool_addresses.iloc[start_index + 1]['id']
        end_ip = pool_addresses.iloc[end_index - 1]['id']
        broad_cast = pool_addresses.iloc[end_index]['id']
        num_ip = end_index - start_index + 1
        records.append((org_id, network, start_ip, end_ip, broad_cast, num_ip))
        start_index = end_index + 1

    return records

def get_pool(pool_addresses, start_index, block_size):
    idx = start_index
    ip_1 = int(ipaddress.ip_address(pool_addresses.iloc[start_index]['ip_address']))

    for i in range(block_size):
        idx = start_index + i
        if int(ipaddress.ip_address(pool_addresses.iloc[start_index]['ip_address'])) - ip_1 > block_size:
            idx -= 1
            break
    return idx


def get_address_blocks(db, org_id):
    query = 'SELECT id, org_id, network, broadcast FROM address_blocks WHERE linked = 0 AND assigned IS NULL AND org_id = {};'
    df = db.getQueryData(query.format(org_id))
    return df

def update_block_ip(db, blocks):
    query1 = "UPDATE ip_addresses SET reserved = ? WHERE id >= ? AND  id <= ?;"
    query2 = "UPDATE address_blocks SET new=? WHERE id=?;"
    records = []
    updates = []
    for idx, row in blocks.iterrows():
        records.append((row['id'], row['network'], row['broadcast']))
        updates.append((0, row['id']))

    cursor = db.conn.cursor()
    cursor.executemany(query1, records)
    db.conn.commit()

    cursor = db.conn.cursor()
    cursor.executemany(query2, updates)
    db.conn.commit()


def save_address_blocks(db, records):
    logging.debug('address records' + str(records))
    query = "INSERT INTO address_blocks (org_id, network, start_ip, end_ip, broadcast, num_ip) VALUES (?,?,?,?,?,?);"
    cursor = db.conn.cursor()
    cursor.executemany(query,records)
    db.conn.commit()

def update_allocation_record(db, id):
    query = 'UPDATE network_allocations SET blocks_created = 1 WHERE id = ?'
    cursor = db.conn.cursor()
    cursor.execute(query, (id,))
    db.conn.commit()

def get_ptp_blocks(org_id, df):
    records = []

    for idx in range(0, len(df), 2):
        ip_a_idx  = df.iloc[idx]['id']
        ip_b_idx = df.iloc[idx + 1]['id']

        ip_a = int(ipaddress.ip_address(df.iloc[idx]['ip_address'].split('/')[0]))
        ip_b = int(ipaddress.ip_address(df.iloc[idx]['ip_address'].split('/')[0]))
        # check to make sure addresses are unit distance
        # note this is not a hard and fast rule, but it is easier for managing connections
        if (ip_b - ip_a) > 1:
            # for now just log a warning
            logging.debug('{0}, {1}, {2}'.format(ip_a, ip_b, ip_b - ip_a))
            logging.warning(" ip addresses not unit distance")
            records.append((org_id, ip_a_idx, ip_b_idx))
        else:
            records.append((org_id, ip_a_idx, ip_b_idx))
    return records

def save_ptp_blocks(db, records):
    logging.debug('ptp update records' + str(records))
    query = "INSERT INTO ptp_blocks (org_id, ip_a, ip_b) VALUES (?,?,?);"
    cursor = db.conn.cursor()
    cursor.executemany(query, records)
    db.conn.commit()

def update_ptp_ips(db, blocks):
    query1 = "UPDATE ip_addresses SET reserved = ? WHERE org_id = ? AND id >= ? AND  id <= ?;"
    query2 = "UPDATE ptp_blocks SET new=? WHERE id=?;"
    records = []
    updates = []
    for idx, row in blocks.iterrows():
        records.append((row['id'], row['org_id'], row['ip_a'], row['ip_b']))
        updates.append((0, row['id']))

    update_records = tuple(updates)
    cursor = db.conn.cursor()
    cursor.executemany(query1, records)
    db.conn.commit()

    cursor = db.conn.cursor()
    cursor.executemany(query2, update_records)
    db.conn.commit()


if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-c', '--club', help='club name')
    parser.add_argument('--club_id', help='club id', default=None)

    parser.add_argument('--ptp_only', help='Assign addresses only to ptp blocks', action='store_true')
    parser.add_argument('--ether_only', help='Assign addresses to ether only', action='store_true')
    parser.add_argument('--blocks_only', help='Assign addresses to address blocks only', action='store_true')
    parser.add_argument('--db', help='configuration db', required=True)
    parser.add_argument('-l', '--log', default = None, help='logging file, default will be system name')

    if TEST == True:
        args= parser.parse_args(['-c','example_club', '--db', '../data/planning_example.sqlite3'])
        #args = parser.parse_args(['-c', 'spokane','--db', '../data/planning_spokane.sqlite3'])
    else:
        args = parser.parse_args()

    if (args.club is None and args.club_id is None):
        print("You must define either a club name or club id")
        parser.print_help()
        parser.exit()

    main(args)