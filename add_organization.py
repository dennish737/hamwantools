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
Python script to add an organization to the planning DB
"""

def main(args):
    # at a minimum the user must provide a club name. they can do this
    # with a -c | --club option or in a csv file (--csv). If both are
    # provided what?
    check_dirs(['./outputs', './logs'])
    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = './logs/' + 'add organization' + now.strftime("%Y_%m_%d_%H_%M_%S") + ".log"
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))

    db = DbSqlite()
    db.connect(args.db)

    query, records = get_query_args(args)
    #print(query)
    #print(records)
    add_orgs(db.conn,query,records)

def check_dirs(dir_list):
    for d in dir_list:
        if not os.path.isdir(d):
            os.makedirs(d)

def get_query_args(args):
    # normally user will pass in a single item from the command line, or use a csv
    # file. If they set both args.club and args.csv, both will be processed, which may cause an error
    # if the club name in the csv and commandline are not unique
    # db column names for organization table
    db_args = ['state', 'county', 'state_region_id','friendly_name', 'club_name', 'club_contact',
               'ptp_net_size', 'device_net_size', 'block_size', 'share_ptp_net']
    # need one '?' for each value added, total 10
    value_args = 'VALUES(?,?,?,?,?,?,?,?,?,?);'
    query = 'INSERT INTO organizations (' + ','.join(db_args) + ') ' + value_args
    df = pd.DataFrame(columns=db_args)
    records = []
    if args.club is not None:
        # use command line args to build entry
        params = [args.state, args.cnty, args.region, args.friendlynam, args.club,
                  args.contact, args.ptp_size, args.dev_size, args.block,
                  0 if args.share == False else 1]
        records.append(tuple(params))

    if args.csv is not None:
        file = args.csv
        df = pd.read_csv(args.csv)

        # note multiple orgs can be defined
        for i, row in df.iterrows():
            params = []
            for j in range(len(db_args)):
                if db_args[j] in row.keys():
                    params.append(check_defaults(db_args[j], row[db_args[j]]))
                else:
                    params.append(check_defaults(db_args[j], None))
            records.append(tuple(params))
    return query, records

def check_defaults(key, value):
    # check keys
    check_keys = {'ptp_net_size':256, 'device_net_size':256, 'block_size':16, 'share_ptp_net':0}
    share = 0
    if key in check_keys.keys():
        if key == 'share_ptp_net' and value is None:
            value = 0
        elif key == 'share_ptp_net' and value is not None:
            value = 1
        elif value is None:
            value = check_keys[key]
    return value

def add_orgs(conn, query, records):

    cursor = conn.cursor()
    cursor.executemany(query, records )
    conn.commit()


if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-c', '--club', help='club name')
    parser.add_argument('--csv', help='CSV File containing organization information')
    parser.add_argument('-s', '--state', help='State')
    parser.add_argument('--cnty', help='county')
    parser.add_argument('-f', '--friendlynam',help='Organization friendly name. default club name')
    parser.add_argument('--contact', help='Club email address')
    parser.add_argument('-r', '--region', help="state region")
    parser.add_argument('--ptp_size', help='Size of ptp network', default=256)
    parser.add_argument('--dev_size', help='Device network size', default=256)
    parser.add_argument('--block', help='Block Address Size', default=16)
    parser.add_argument('--share', help='Share ptp net with device net.', action='store_true')

    parser.add_argument('--db', help='configuration db', default='./data/netplanning.sqlite3')
    parser.add_argument('-l', '--log', default = None, help='logging file, default will be system name')

    if TEST == False:
        args = parser.parse_args(['-c', 'spokane'])
        #args= parser.parse_args(['--csv','./templates/organization_template.csv'])
        #args = parser.parse_args(['-c', 'spokane','--csv', './templates/organization_template.csv'])
    else:
        args = parser.parse_args()
        if args.club is None and args.csv is None:
            print("You must define either provide a club name (-c | --club) or a csv file (--csv) - exiting")
            parser.print_help()
            parser.exit()

    main(args)