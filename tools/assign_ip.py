# This tool will auto auto assign ip addresses to equipment an paths

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
import numpy as np
import ipaddress

import logging
from parsers.dbtools import DbSqlite

def main(args):
    check_dirs(['../outputs', '../logs'])
    org_id = args.club_id
    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = '../logs/' + 'assign_ip_addresses' + now.strftime("%Y_%m_%d_%H_%M_%S") + ".log"
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





if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-c', '--club', help='club name')
    parser.add_argument('--club_id', help='club id', default=None)

    parser.add_argument('--ptp_only', help='Assign addresses only yo ptp blocsk', action='store_true')
    parser.add_argument('--ether_only', help='Assign addresses to ether only', action='store_true')
    parser.add_argument('--blocks_only', help='Assign addresses to address blocks on;y', action='store_true')
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