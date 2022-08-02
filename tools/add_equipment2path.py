# tool to add equipment to one or more paths
# by default, this tool will read the paths assigned to an org, and add equipment to all
# paths where equipment is not defined and equipment is available at a site
import argparse
from argparse import ArgumentParser

import os
import sys
import datetime

from datetime import datetime
import pandas as pd
import numpy as np

import logging

# need ot set include path to parent directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
from libs.dbtools import DbSqlite

def main(args):
    dirs = check_dirs(['outputs', 'logs'])
    out_dir = dirs[0]
    log_dir = dirs[1]

    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = os.path.join(log_dir, ('add_equipment2path' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.log'))
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))

    db = DbSqlite()
    db.connect(args.db)

    org_id = db.getOrganizationId(args.club)
    logging.info("adding equipment to path for organization={0} ,org_id = {1}".format(args.club, org_id))

    if args.path is not None:
        # user want to add equipment to a specific path
        logging.info("adding equipment to path {0} ".format(args.path))
        query = 'SELECT * FROM paths WHERE org_id = {0} AND name = {1};'
        path_data = db.getQueryData(query.format(org_id, args.path))
        if len(path_data) > 0:
            prosess_path_equipment(db, org_id, path_data, equip_a=args.equip_a, equip_b=args.equip_b)
        else:
            logging.error("path {} does not exist".format(args.parh))
            exit(1)
    else:
        # assign equipment to all paths needing equipment
        logging.info("adding equipment to all paths for org_id = {0} ".format(org_id))
        query = 'SELECT * FROM paths WHERE org_id = {};'
        path_data = db.getQueryData(query.format(org_id))
        if len(path_data) > 0:
            process_path_equipment(db, org_id, path_data)
        else:
            logging.error("No paths defined for organization = {}".format(args.club))
            exit(1)

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

def process_path_equipment(db, org_id, paths, equip_a=None, equip_b=None):
    logging.info("starting process_path_equipment, org_id={0}, paths={1}".format(org_id,paths))
    for idx, row in paths.iterrows():
        path_id = row['id']
        if equip_a is None:
            if row["device_a"] is None:
                logging.info("get the first ptp device for site = {0}".format(row['site_a']))
                id_a, name_a = db.getFirstAvailablePTP(row['site_a'])
            else:
                name = db.getEquipmentName(row['device_a'])
                logging.warning("Equipment for path {0} already assigned: {1}".format(row['name'], name))
                id_a = row["equip_a"]
                name_a = name
        else:
            new_id_a, new_name_a = db.getEquipmentId(org_id, equip_a)
            if row["device_a"] is None and new_id_b is not None:
                id_b = new_id_a
                name_b = new_name_a
            else:
                if row['device_b'] is not None and new_id_a is not None:
                    name = db.getEquipmentName(row['device_a'])
                    logging.warning("Equipment for path {0} already assigned: {1}".format(row['name'], name))
                    id_a = row["device_b"]
                    name_a = name

        if equip_b is None:
            if row["device_b"] is None:
                id_b, name_b = db.getFirstAvailablePTP(row['site_b'])
            else:
                name = db.getEquipmentName(row['device_b'])
                logging.warning("Equipment for path {0} already assigned: {1}".format(row['name'], name))
                id_b = row["device_a"]
                name_b = name
        else:
            new_id_b, new_name_b = db.getEquipmentId(org_id, equip_a)
            if row["device_a"] is None and new_id_b is not None:
                id_b = new_id_b
                name_b = new_name_b
            else:
                if row['device_b'] is not None and new_id_b is not None:
                    name = db.getEquipmentName(row['device_b'])
                    logging.warning("Equipment for path {0} already assigned: {1}".format(row['name'], name))
                    id_b = row["equip_b"]
                    name_b = name

        logging.debug("path= {0}, id_a= {1}, id_b= {2}".format(path_id, id_a, id_b))
        db.assignEquipmentToPTPPath(path_id, id_a, id_b)
        logging.info("path {0} equipment updated")

if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-c', '--club', help='club name',required=True)
    parser.add_argument('--path', help='path Name', default=None)
    parser.add_argument('--site', help='site name where equipment is located', default=None)
    parser.add_argument('--equip_a', help="assign specific equipment, by name to a path.equip_a", default=None)
    parser.add_argument('--equip_b', help="assign specific equipment, by name to a path.equip_b", default=None)

    parser.add_argument('--db', help='configuration db', required=True)
    parser.add_argument('-l', '--log', default=None, help='logging file, default will be system name')

    if TEST == True:
        args= parser.parse_args(['-c', 'example_club', '--db', '../data/planning_example.sqlite3'])
        #args = parser.parse_args(['-c', 'spokane', '--db', '../data/spokane_example.sqlite3'])
    else:
        args = parser.parse_args()

    main(args)