import argparse
import traceback
from argparse import ArgumentParser

import os
import datetime
import sys
import re
import sqlite3
import requests
import json
from datetime import datetime
import pandas as pd
import ipaddress

import logging
from parsers.dbtools import DbSqlite

"""
python script to divide an ip address allocation into blocks
"""
# dict <CIDR>:<num_addresses>
block_sizes = {16:65536,17:32768,18:16384, 19:8192, 20:4096, 21:2048, 22:1024, 23:512, 24:256, 25:128, 26:64, 27:32, 28:16}


def main(args):
    check_dirs(['./outputs', './logs'])
    org_id = args.club_id
    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = './logs/' + 'add_ipaddresses' + now.strftime("%Y_%m_%d_%H_%M_%S") + ".log"
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))
    # enable sqlite np.int64
    sqlite3.register_adapter(np.int64, lambda val: int(val))
    sqlite3.register_adapter(np.int32, lambda val: int(val))

    db = DbSqlite()
    db.connect(args.db)

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
    df = get_unblocked_network_allocations(org_id, db.conn)
    print("allocations = ", df)
    count = 0
    skip_ptp = args.skip_ptp
    skip_dev = args.skip_dev
    ip_types = {'pool':1, "ptp":2, "device":3}
    for i, row in df.iterrows():
        allocation_id = row['id']

        addresses = generate_ip(row)
        records = []
        device_offset = device_net_size if not args.skip_dev else 0
        ptp_offset = (ptp_size + device_offset) if not args.skip_ptp else 0
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
        save_addresses(db.conn, records)
        # add CIDR /31 to ptp addresses
        update_ptp_addresses(db.conn)

    # create address pools (blocks)
    # get the address to pool
    ip_addresses = get_pool_addresses(db, org_id)
    address_blocks = generate_pool_blocks(ip_addresses, org_id, organization_params['block_size'])


    save_address_blocks(db.conn,address_blocks)

    reserve_pool_ips(db.conn,reserved_for_pools)

    db.close()

def check_dirs(dir_list):
    for d in dir_list:
        if not os.path.isdir(d):
            os.makedirs(d)

def get_unblocked_network_allocations( id, conn):
    query = 'select * from network_allocations where blocks_created = 0 and org_id = {}'
    df = pd.read_sql(query.format(id), conn)
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


def save_addresses(conn, records):
    query = 'INSERT INTO ip_addresses (org_id, ip_address, ip_type) VALUES(?,?,?);'
    cursor = conn.cursor()
    cursor.executemany(query,records)
    conn.commit()

def update_ptp_addresses(conn):
    query = 'UPDATE ip_addresses set ip_address = ip_address || "/31" where ip_type = (select id from ip_types where type_name = "ptp");'
    cursor =conn.cursor()
    cursor.execute(query)
    conn.commit()

def get_pool_addresses(db, org_id):
    query = """SELECT id, org_id, ip_address FROM ip_addresses 
        WHERE ip_type = (select id from ip_types where type_name = "pool" AND reserved = 0 and org_id = {});"""
    df = db.getQueryData(query.format(org_id))
    return df

def generate_pool_blocks( df, org_id,block_size):
    # we are going to create block in increments of 16 address
    # the addresses must be continuous but available address space may
    # not be so check.
    start_index = 0
    records = []
    reserver = []
    while start_index < len(df):
        end_index = get_pool(df, start_index, block_size)
        network = df.iloc[start_index]['id']
        start_ip = df.iloc[start_index + 1]['id']
        end_ip = df.iloc[end_index - 1]['id']
        broad_cast = df.iloc[end_index]['id']
        num_ip = end_index - start_index + 1
        start_ip_id = df.iloc[start_index]['id']
        end_ip_id = df.iloc[end_index]['id']

        records.append((org_id, network, start_ip, end_ip, broad_cast, num_ip))
        reserver.append((start_ip_id, end_ip_id))
        start_index = end_index + 1

    return records


def get_address_blocks(db, org_id):
    query = 'SELECT id, org_id, network, broadcast FROM address_blocks WHERE linked = 0 AND assigned IS NULL AND org_id = {};'
    df = db.getQueryData(query.format(org_id))
    return df

def build_ip_address_updates(df):
    records = []
    for index, row in df.iterrows():
        records.append((row['id'], row['network'], row['broadcast']))
    return records

def reserve_pool_ips(conn, records):
    query = "UPDATE ip_addresses SET reserved = ? WHERE id >= ? and  id <= ?;";
    cursor = conn.cursor()
    cursor.executemany(query,records)
    conn.commit()


def save_address_blocks(conn, records):
    print(records)
    query = "INSERT INTO address_blocks (org_id, network, start_ip, end_ip, broadcast, num_ip) VALUES (?,?,?,?,?,?);"
    cursor = conn.cursor()
    cursor.executemany(query,records)
    conn.commit()

def update_allocation_record(conn, id):
    query = 'UPDATE network_allocations SET blocks_created = 1 WHERE id = ?'
    cursor = conn.cursor()
    cursor.execute(query, (id,))
    conn.commit()




if __name__ == '__main__':

    TEST = True
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-c', '--club', help='club name')
    parser.add_argument('--club_id', help='club id')
    parser.add_argument('--skip_ptp', help='skip assigning addresses for ptp network', action='store_true')
    parser.add_argument('--skip_dev', help='skip assigning addresses for dev network', action='store_true')
    parser.add_argument('--db', help='configuration db', default='./data/netplanning.sqlite3')
    parser.add_argument('-l', '--log', default = None, help='logging file, default will be system name')

    if TEST == True:
        args= parser.parse_args(['-c','spokane'])
    else:
        args = parser.parse_args()

    if (args.club is None and args.club_id is None):
        print("You must define either a club name or club id")
        parser.print_help()
        parser.exit()

    main(args)