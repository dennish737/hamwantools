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
tool to add one or more paths to an organization site
"""

db = None

def main(args):
    global db
    check_dirs(['./outputs', './logs'])
    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = './logs/' + 'create_blocks' + now.strftime("%Y_%m_%d_%H_%M_%S") + ".log"
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))

    db = DbSqlite()
    db.connect(args.db)

    org_id = db.getOrganizationId(args.club)
    _type = db.getPathType(args.type)

    site_query = 'SELECT id, name FROM sites'
    site_data = db.getQueryData(site_query)

    query, records = get_query_args(args, org_id, site_data, _type)

    #add_paths(db.conn,query, records)
    print(query)
    print(records)
    db.close()

def check_dirs(dir_list):
    for d in dir_list:
        if not os.path.isdir(d):
            os.makedirs(d)

def get_query_args(args, org_id, site_data, _type):
    # normally user will pass in a single item from the command line, or use a csv
    # file. If they set both args.club and args.csv, both will be processed, which may cause an error
    # if the club name in the csv and commandline are not unique
    # db column names for organization table
    db_args = ['type_id', 'site_a', 'site_b', 'name']
    # need one '?' for each value added, total 4
    value_args = 'VALUES(?,?,?,?);'
    query = 'INSERT INTO paths ( org_id, ' + ','.join(db_args) + ') ' + value_args

    records = []
    if args.site1 is not None and args.site2 is not None:
        # use command line args to build entry
        site_a = site_data[site_data['name'] == args.site1 ]['id'].tolist()[0]
        site_b = site_data[site_data['name'] == args.site2 ]['id'].tolist()[0]
        params = [org_id, _type, site_a, site_b,
                  args.name ]
        records.append(tuple(params))

    if args.csv is not None:
        file = args.csv
        df = pd.read_csv(args.csv)

        # note multiple orgs can be defined
        for i, row in df.iterrows():
            params = [org_id]
            print("row.keys()=", row.keys())
            for j in range(len(db_args)):
                if db_args[j] in row.keys():
                    if db_args[j] == 'site_a' or db_args[j] == 'site_b':
                        # parameter is a site name
                        site = site_data[site_data['name'] == row[db_args[j]]]['id'].tolist()[0]
                        params.append(check_defaults(db_args[j], site, _type))
                    else:
                        params.append(check_defaults(db_args[j], row[db_args[j]], _type))
                else:
                    params.append(check_defaults(db_args[j], None, _type))
            records.append(tuple(params))
    return query, records

def check_defaults(key, value, _type):
    global db
    # check keys
    check_keys = {'type_id': _type}
    share = 0
    if key in check_keys.keys():
        if value is None:
            value = check_keys[key]
        else:
            value = db.getPathType(value)
    return value

def add_paths(conn, query, records):

    cursor = conn.cursor()
    cursor.executemany(query, records )
    conn.commit()

if __name__ == '__main__':

    TEST = True
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-c', '--club', help='club name',required=True)
    parser.add_argument('--site1', help='Site Name for site 1')
    parser.add_argument('--site2', help='Site Name for site 2')
    parser.add_argument('--name', help='path name')
    parser.add_argument('--csv', help='CSV File containing path information')
    parser.add_argument('--type', default='BPTP', const='BPTP',
                        nargs='?',
                        choices=["BPTP", "CPTMP", "CPTP"],
                        help='Site type: BPTP | CPTMP | CPTP  (default: %(default)s')

    parser.add_argument('--db', help='configuration db', default='./data/netplanning.sqlite3')
    parser.add_argument('-l', '--log', default = None, help='logging file, default will be system name')

    if TEST == True:
        #args = parser.parse_args(['-c', 'spokane', '--site1', 'SPODEM', '--site2', 'Krell'])
        args= parser.parse_args(['-c', 'spokane', '--csv','./templates/path_template.csv'])
        #args = parser.parse_args(['-c', 'spokane', '--site1', 'SPODEM', '--site2', 'Krell','--csv',
        #    './templates/site_template.csv', '--name', 'Krell'])
    else:
        args = parser.parse_args()
        if args.name is None and args.csv is None:
            print("You must define either provide site name (--name) or a csv file (--csv) - exiting")
            parser.print_help()
            parser.exit()

    main(args)