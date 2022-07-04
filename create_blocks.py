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
        log_file = './logs/' + 'create_blocks' + now.strftime("%Y_%m_%d_%H_%M_%S") + ".log"
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))

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
    for i, row in df.iterrows():
        allocation_id = row['id']
        address_blocks = generate_network_blocks(row, organization_params['block_size'])
        # locate index for ptp block

        device_offset = device_net_size/block_size if not args.skip_dev else 0
        ptp_offset = (ptp_size/block_size + device_offset) if not args.skip_ptp else 0
        ptp_index = len(address_blocks) - ptp_offset -1
        dev_index = len(address_blocks) - device_offset -1
        #print("number of address_blocks:",len(address_blocks))
        #print("ptp_index = ", ptp_index)
        #print("dev_index = ", dev_index)
        # add blocks to the database
        # columns: org_id, start_address, end_address, num_addresses, start_ip_num, end_ip_num
        records = []
        for i in range(len(address_blocks)):
            address_block = address_blocks[i]
            reserved = None
            if i > ptp_index:
                reserved = 'PTP'
            if i > dev_index:
                reserved = 'device'
            records.append((org_id, address_block[0], address_block[1], block_size,
                            int(ipaddress.ip_address(address_block[0])), int(ipaddress.ip_address(address_block[1])),
                            reserved))

        save_blocks(db.conn, records)
        update_allocation_record(db.conn, allocation_id)
    db.close()

def check_dirs(dir_list):
    for d in dir_list:
        if not os.path.isdir(d):
            os.makedirs(d)

def get_unblocked_network_allocations( id, conn):
    query = 'select * from network_allocations where blocks_created = 0 and org_id = {}'
    df = pd.read_sql(query.format(id), conn)
    return df

def generate_network_blocks(row, block_size):
    ip_start = int(ipaddress.ip_address(row['starting_address']))
    ip_end = int(ipaddress.ip_address(row['ending_address']))

    num_addr = get_number_of_addresses(ip_start, ip_end)
    blocks = []
    for i in range(0, num_addr, block_size):
        block = generate_block(ip_start + i, block_size)
        blocks.append(block)
    return blocks

def get_number_of_addresses(start, end):
    ip_start = int(ipaddress.ip_address(start))
    ip_end = int(ipaddress.ip_address(end))
    num_addresses = ip_end - ip_start + 1
    return num_addresses

def generate_block(start, size):
    ip_start = str(ipaddress.ip_address(start))
    ip_end = str(ipaddress.ip_address(start + (size - 1)))
    return [ip_start, ip_end]

def save_blocks(conn, records):
    query = 'INSERT INTO address_blocks (org_id, start_address, end_address, num_addresses, start_ip_num, end_ip_num, reserved) VALUES(?,?,?,?,?,?,?);'
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