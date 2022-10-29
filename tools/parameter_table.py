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
from libs.dbtools import DbSqlite
from libs.map_tables import MapTables
from libs.ip_tools import ip2long, ip2hex, int2ip, hex2ip

description = """Parameter_table - maps database names to templates names"""

# initialize mapping tables
map_tables = MapTables()
dhcp_dict = map_tables.GetDHCPDict()
map_dict = map_tables.GetMapDict()

def main(args):
    dirs = check_dirs(['outputs', 'logs'])
    out_dir = dirs['outputs']
    log_dir = dirs['logs']

    log_file = args.log
    now = datetime.now()

    if args.log is None:
        log_file = os.path.join(log_dir, ('basic_parser' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.log'))
    print(log_file)

    level = get_log_level(args.log_level)
    level = logging.DEBUG
    logging.basicConfig(filename=log_file, encoding='utf-8', level=level)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))

    db = DbSqlite()
    db.connect(args.db)

    org_id = db.getOrganizationId(args.club)
    if org_id is None:
        logging.info(f"unable to find org_id for {args.club}")
        exit(1)
    call_sign = db.getOrganizationCallSign(org_id)
    if call_sign:
        call_sign += '/'
    print("call sign = ", call_sign)

    site_ids = None
    if args.site:
        logging.info("getting ids for site: {0}".format(args.site))
        site_ids = []
        #get ids for each site
        site_ids.append(db.getSiteId(org_id, args.site))
    else:
        logging.info(f"no site specified for  {args.club}")
        exit(1)
    print('Site Name:', args.site.lower())
    print('site_ids =', site_ids)
    print('Device name:', args.device.lower())
    out_file = '../outputs/' + args.device.lower() + '.prm'
    device_id = db.getEquipmentId(org_id, args.device)[0]
    print('Device id:', device_id)

    #print("parameters -------------")
    map_params = get_parameters(device_id, call_sign, db)
    #print(map_params)
    global_params = get_globals(org_id, site_ids[0], db)
    print(global_params)
    for k, v in global_params.items():
        map_params[k] = v
    security_params = get_security(org_id,site_ids[0], db)
    #print(security_params)
    for k, v in security_params.items():
        map_params[k] = v

    with open(out_file, 'w') as output:
        print('        Tag                   Param                ', file=output)
        #print('---------------------------------------------------', file=out_file)
        for k,v in map_params.items():
            print('{0: <25} {1}'.format(k, v), file=output)




def find_base_dir():
    base_dir = None
    path = os.getcwd()
    i = 0
    while i > -1 and i < 3:
        print(path)
        item_list = os.listdir(path)
        if 'tools' in item_list:
            print('found:')
            base_dir = path
            i = -1
            break
        else:
            i += 1
            path = os.path.dirname(path)
    return base_dir

def check_dirs(dir_list):
    dirs = {}
    base_dir = find_base_dir()
    for d in dir_list:
        print(d)
        path = os.path.join(base_dir, d)
        if not os.path.isdir(path):
            os.makedirs(d)
            dirs[d] = path
            print('directory {0} created'.format(path))
        else:
            dirs[d] = path
    return dirs


def get_log_level(level):
    log_level = logging.WARNING
    if level == 'debug':
        log_level = logging.DEBUG
    elif level == 'info':
        log_level = logging.INFO
    elif level == 'error':
        log_level = logging.ERROR
    elif level == 'critical':
        log_level = logging.CRITICAL
    else:
        log_level = logging.WARNING
    return log_level


def dhcp_params(params, param_dict):
    # process dhcp info
    for param_set in params:
        for k,v in dhcp_dict.items():
            #print(k,v)
            if v in param_set:
                param_dict[k] = param_set[v]
    return

def get_parameters(device_id, call_sign, db):
    params = db.getDeviceParameters(device_id, call_sign)
    logging.info("parameters returned: ------------------------------")
    for param, value in params.items():
        logging.info("params %s: %r", param, value)

    map_params = {}
    for k, v in map_dict.items():
        if v in params:
            if v == 'dhcp':
                dhcp_params(params[v], map_params)
            else:
                map_params[k] = params[v]

    logging.info("mapped parameters: ---------------------------------")
    for param, value in map_params.items():
        logging.info("mapped params %s: %r", param, value)

    map_gparams = {}

    return map_params

def get_globals(org_id, site_id,db):
    g_params = db.getGlobalParameters( org_id, site_id)
    logging.info("global parameters returned: ------------------------------")
    for gparam, value in g_params.items():
        logging.info("global params %s: %r", gparam, value)
    map_gparams = {}
    for k, v in map_dict.items():
        if v in g_params:
            map_gparams[k] = g_params[v]
    print(g_params)
    #print(map_gparams)
    return map_gparams

def get_security(org_id, site_id, db):
    security_params = db.getSecurityParameters(org_id, site_id)
    for s_param, value in security_params.items():
        logging.info("security params %s: %r", s_param, value)

    map_sparams = {}
    for k, v in map_dict.items():
        if v in security_params:
            map_sparams[k] = security_params[v]
    #print(security_params)
    #print(map_sparams)
    return map_sparams

if __name__ == '__main__':

    TEST = False
    args = None
    parser: ArgumentParser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--club', help='club name', required=True)
    parser.add_argument('--site', help='the name of the site ', required=True)
    parser.add_argument('--device', help='device_name', required=True)
    parser.add_argument('--db', help='configuration db', required=True)

    parser.add_argument('templates', nargs='+', help='a list of templates, at least one required' )

    parser.add_argument('--configs', default='router', const='router',
                        nargs='?',
                        choices=["router", "sector", "bptp", "gateway", 'default_gateway', 'client'],
                        help='Create config files for:[ router | sector | bptp | gateway | default_gateway | client ] (default: %(default)s')


    parser.add_argument('-l', '--log', default=None, help='logging file, default will be system name')
    parser.add_argument('--log_level', default='warning', const='warning',
                        nargs='?',
                        choices=["debug", "info", "warning", "error", "critical"],
                        help='assign loging level')

    if TEST == True:
        #in_args = ['-c', 'example_club','--db', '../data/planning_example.sqlite3']
        in_args = ['-c', 'spokane', '--db', '../data/spokane_example.sqlite3', '--device', 'r1.KRELL', '--site', 'krell', '--configs', 'router',
                   '../templates/r_router_template.txt']
        args = parser.parse_args(in_args)
    else:
        args = parser.parse_args()

    # check and make sure we have the correct number of templates

    main(args)
    #print(args)