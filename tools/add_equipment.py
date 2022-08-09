
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
from libs.dbtools import DbSqlite

"""
tool to add one or more sites to an organization
"""
db = None

def main(args):
    dirs = check_dirs(['outputs', 'logs'])
    out_dir = dirs[0]
    log_dir = dirs[1]

    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = os.path.join(log_dir, ('add_equipment' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.log'))
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))


    db = DbSqlite()
    db.connect(args.db)

    org_id = db.getOrganizationId(args.club)
    df = pd.read_csv(args.csv)
    records = build_equipment_records(db, org_id, df)
    add_equipment(db, records)

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

def build_equipment_records(db, org_id, df):
    records = []
    for i, row in df.iterrows():
        site_id = db.getSiteId(org_id, row['site'])
        group_id, suffix = db.getEquipmentGroup(row['group'])
        routers, sectors, ptp = db.getSiteEquipmentCounts(site_id)
        name = row['site']
        if suffix in ['R', 'r']:
            name = suffix + str(routers +1) + '.' + row['site']
            db.updateSiteRouterCount(site_id, routers + 1)
        elif suffix in ['GW', 'gw']:
            name = suffix + str(routers +1) + '.' + row['site']
            db.updateSiteRouterCount(site_id, routers + 1)
        elif suffix in ['S', 's']:
            name = suffix + str(sectors + 1) + '.' + row['site']
            db.updateSiteSectorCount(site_id, sectors + 1)
        elif suffix in ['PTP', 'ptp']:
            name = suffix + str(ptp +1) + '.' + row['site']
            db.updateSitePTPCount(site_id,ptp + 1)
        records.append((site_id, group_id, name, row['serial_num'], row['model'] ))
    return(records)

def add_equipment(db, records):
    # need one '?' for each value added, total 5
    value_args = 'VALUES(?,?,?,?,?);'
    query = 'INSERT INTO site_equipment ( site_id, group_id, name, serial_num, model) ' + value_args
    cursor = db.conn.cursor()
    cursor.executemany(query, records )
    db.conn.commit()



if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-c', '--club', help='club name',required=True)
    parser.add_argument('--csv', help='CSV File containing site information')
    parser.add_argument('--db', help='configuration db', required=True)
    parser.add_argument('-l', '--log', default = None, help='logging file, default will be system name')

    if TEST == True:
        in_args = ['-c', 'example_club', '--csv','../examples/equipment_example.csv','--db', '../data/planning_example.sqlite3']
        #in_args = ['-c', 'spokane','--csv', '../examples/equipment_spokane.csv', '--db', '../data/spokane_example.sqlite3']
        args = parser.parse_args(in_args)
    else:
        args = parser.parse_args()


    main(args)