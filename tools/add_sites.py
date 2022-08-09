import argparse
from argparse import ArgumentParser

import sys
import os
import datetime
import sqlite3

from datetime import datetime
import pandas as pd
import numpy as np

import logging

# need ot set include path to parent directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
from libs.dbtools import DbSqlite

"""
tool to add one or more sites to an organization
"""
db = None

def main(args):
    global db
    dirs = check_dirs(['outputs', 'logs'])
    out_dir = dirs[0]
    log_dir = dirs[1]
    print("dirs = ",dirs)
    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = os.path.join(log_dir, ('add_sites' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.log'))
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))

    db = DbSqlite()
    db.connect(args.db)

    org_id = db.getOrganizationId(args.club)
    _type = db.getSiteType(args.type)

    query, records = get_query_args(args, org_id, _type)
    add_sites(db.conn,query, records)
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

def add_sites(conn, query, records):

    cursor = conn.cursor()
    cursor.executemany(query, records )
    conn.commit()

def get_query_args(args, org_id, _type):
    # normally user will pass in a single item from the command line, or use a csv
    # file. If they set both args.club and args.csv, both will be processed, which may cause an error
    # if the club name in the csv and commandline are not unique
    # db column names for organization table
    db_args = ['site_type', 'name', 'owner', 'contact', 'lat', 'lon']
    # need one '?' for each value added, total 7
    value_args = 'VALUES(?,?,?,?,?,?,?);'
    query = 'INSERT INTO sites ( org_id, ' + ','.join(db_args) + ') ' + value_args

    df = pd.DataFrame(columns=db_args)
    records = []
    if args.name is not None:
        # use command line args to build entry
        params = [org_id, _type, args.name, args.owner,
                  args.contact, args.lat, args.lon ]
        records.append(tuple(params))

    if args.csv is not None:
        file = args.csv
        df = pd.read_csv(args.csv)

        # note multiple orgs can be defined
        for i, row in df.iterrows():
            params = [org_id]
            for j in range(len(db_args)):
                if db_args[j] in row.keys():
                    params.append(check_defaults(db_args[j], row[db_args[j]], _type))
                else:
                    params.append(check_defaults(db_args[j], None, _type))
            records.append(tuple(params))
    return query, records

def check_defaults(key, value, _type):
    global db
    # check keys
    check_keys = {'site_type': _type}
    share = 0
    if key in check_keys.keys():
        if value is None:
            value = check_keys[key]
        else:
            value = db.getSiteType(value)
    return value

if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-c', '--club', help='club name',required=True)
    parser.add_argument('-s', '--site', help='Site Name')
    parser.add_argument('--csv', help='CSV File containing site information')
    parser.add_argument('--type', default='CELL', const='CELL',
                        nargs='?',
                        choices=["CELL", "CLIENT", "GATEWAY"],
                        help='Site type: CELL | CLIENT | GATEWAY  (default: %(default)s')
    parser.add_argument('--name', help='Site Name')
    parser.add_argument('--owner',help='Owner of the site')
    parser.add_argument('--contact', help='Owner Contact Information')
    parser.add_argument('--lat', help='Site latitude in decimal degrees')
    parser.add_argument('--lon', help='Site longitude in decimal degrees')

    parser.add_argument('--db', help='configuration db', required=True)
    parser.add_argument('-l', '--log', default = None, help='logging file, default will be system name')

    if TEST == True:
        in_args = ['-c', 'example_club', '--csv','../examples/site_example.csv','--db', '../data/planning_example.sqlite3']
        #in_args = ['-c', 'spokane','--csv', '../examples/sites_spokane.csv', '--db', '../data/spokane_example.sqlite3']
        args = parser.parse_args(in_args)
    else:
        args = parser.parse_args()
        if args.name is None and args.csv is None:
            print("You must define either provide site name (--name) or a csv file (--csv) - exiting")
            parser.print_help()
            parser.exit()

    main(args)