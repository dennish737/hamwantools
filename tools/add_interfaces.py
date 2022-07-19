
import argparse

from argparse import ArgumentParser

import os
import sys
import datetime

import sqlite3

from datetime import datetime
import pandas as pd
import numpy as np

import logging

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
from parsers.dbtools import DbSqlite

def main(args):
    dirs = check_dirs(['outputs', 'logs'])
    out_dir = dirs[0]
    log_dir = dirs[1]

    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = os.path.join(log_dir, ('add_paths' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.log'))
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))

    db = DbSqlite()
    db.connect(args.db)

    org_id = db.getOrganizationId(args.club)
    site_id = None
    if args.site is not None:
        site_id = db.getSiteId(org_id, args.site)

    df = db.getSiteAvailableEquipmentInterfaces(org_id, site_id=site_id)

    records = []
    for idx, row in df.iterrows():
        record = (row['e_id'], row['if_type'], row['if_name'])
        records.append(record)

    query = 'INSERT OR IGNORE INTO interfaces (equip_id, if_type, if_name) VALUES (?,?,?);'
    cursor = db.conn.cursor()
    cursor.executemany(query, records)
    db.conn.commit()
    cursor.close()



def check_dirs(dir_list):
    global base_dir
    dirs = []
    for dir in dir_list:
        path = os.path.join(base_dir, dir)
        if not os.path.isdir(path):
            os.makedirs(path)
        dirs.append(path)
    return dirs



if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-c', '--club', help='club name',required=True)
    parser.add_argument('-s', '--site',  help='Site Name', default=None)
    parser.add_argument('--db', help='configuration db', required=True)
    parser.add_argument('-l', '--log', default = None, help='logging file, default will be system name')

    if TEST == True:
        in_args = ['-c', 'example_club','--db', '../data/planning_example.sqlite3']
        #in_args = ['-c', 'spokane','--csv', '--db', '../data/planning_spokane.sqlite3']
        args = parser.parse_args(in_args)
    else:
        args = parser.parse_args()


    main(args)