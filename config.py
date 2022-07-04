
# Licensed under the MIT License.

import argparse
import traceback
from argparse import ArgumentParser

import paramiko
import os
import datetime
import sys
import re
import sqlite3
import requests
import json
from datetime import datetime
import pprint
from typing import NamedTuple

from commands.basiccommand import BasicCommand
from commands.fwnat import FWNat
from commands.dns import DNS
from commands.files import Files
from commands.fwrules import FW
from commands.identity import Identity
from commands.interfaces import Interfaces
from commands.ports import Ports
from commands.proxy import Proxy
from commands.scheduler import Scheduler
from commands.socks import Socks
from commands.users import Users
from commands.version import Version

from parsers.dbtools import DbSqlite
from parsers.parseglobal_ip import ParseGlobalIP
from parsers.parseinterface import ParseInterfaces
from parsers.parserouting import ParseRouting
from parsers.parsesnmp import ParseSNMP
from parsers.parsesystem import ParseSystem

import query_nvd

import logging

# CVES_PATH = './assets/mikrotik_cpe_match.json'

sections = {'interfaces': ParseInterfaces, 'routing': ParseRouting, 'snmp': ParseSNMP, 'global_ip': ParseGlobalIP,
            'system': ParseSystem}

def main(args):
    mode = args.mode

    device_name = args.sys_name
    region = args.region

    now = datetime.now()
    check_dirs(['./outputs', './logs'])
    log_file = args.log
    if args.log is None:
        log_file = './logs/' + device_name + now.strftime("%Y_%m_%d_%H_%M_%S") + ".log"
    print(log_file)

    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
    logging.info('Started" {}'.format(now.strftime("%H_%M_%S")))

    db = DbSqlite()
    db.connect(args.db)
    ip, device_type = db.getDeviceIP(args.sys_name)
    print(device_name, ip, device_type)

    out_file = './outputs/' + args.sys_name + '.config'

    logging.info(f"mode={mode}")
    logging.info("device type ={}".format(device_type))
    logging.info("database = {}".format(args.db))
    logging.info("database = {}".format(args.db))
    template_file = args.template
    logging.info("template =".format(template_file))
    logging.info("region ={}".format(region))
    logging.info("device name ={}".format(device_name))
    logging.info("device ip={}".format(ip))
    logging.info("out_file = {}".format(out_file))

    region_params = db.getRegionInfo(region)
    logging.info("region parameter")
    logging.info(region_params)
    logging.info("--------------------------------")

    router_params = None
    if device_type == 'PTP':
        router_params = db.getPTPParams(device_name)
        logging.info("region parameter")
        logging.info(router_params)
        logging.info("----------------------------")

    if args.check_dev:
        all_data = {}
        try:
            # check if the device is connected to the network:
            with paramiko.SSHClient() as ssh_client:
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=ip, port=args.port, username=args.userName, password=args.password,
                                   look_for_keys=False, allow_agent=False)
                command = Identity()
                res = command.run_ssh(ssh_client)
                all_data[command.__name__] = res

                if args.J:
                    print(json.dumps(all_data, indent=4))
                else:
                    print_txt_results(all_data, args.concise)
            # check if we need an additional test
        except Exception as e:
            logging.debug("Device:{0}, at IP:{1}, not found")
            # at this point we may want to terminate
            device_connected = False

    logging.info("Checking attached system")
    logging.info("Building config file {}".format(out_file))

    with open(out_file, 'w') as output:
        for section, value in sections.items():
            logging.debug('Processing {}'.format(section))
            p = value(mode,device_type, template_file)
            p.addParameters(region_params, router_params)

            interfaces = p.getTypeList()

            commands = []

            if section in ['interfaces', 'routing']:
                for interface in interfaces:
                    logging.debug("processing interface = {}".format(interface))
                    activities = p.getActivities(interface)
                    for activity in activities:
                        commands.extend(p.parseSettings(interface, activity, region_params, router_params ))
            else:
                activities = p.getActivities()
                for activity in activities:
                    commands.extend(p.parseSettings(activity, region_params, router_params))

            for command in commands:
                print(command, file=output)

    logging.info("Config file {} created".format(out_file))
    print("Config file {} created".format(out_file))

    if args.ip is not None:
        try:
            logging.info("Checking for device device")
            with paramiko.SSHClient() as ssh_client:
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=args.ip, port=args.port, username=args.userName, password=args.password,
                                   look_for_keys=False, allow_agent=False)
                process_commands(ssh_client, out_file)
                shh_client.close()
        except Exception as e:
                logging.info("Unable to connect to device exiting:")
                print("Unable to connect to device exiting:")
    else:
        logging.info("No device address available. exiting.")
        print("No device address available. exiting.")
    db.close()

def check_dirs(dir_list):
    for d in dir_list:
        if not os.path.isdir(d):
            os.makedirs(d)

def process_commands(ssh_client, out_file):

    with open(out_file, 'r') as config:
        commands = BasicCommand()
        line = config.readline()
        cnt = 1
        while line:
            res = commands.rsh_ssh_ascii(ssh_client, line.strip())
            logging.info('command:' + line.strip() + ' results:' + res)
            print('command:' + line.strip() + ' results:' + res)
            line = config.readline()
            cnt + 1
    logging.info("config loaded")
    return(cnt)

def print_txt_results(res, concise):
    for command in res:
        if (not concise and res[command]["raw_data"]) or res[command]["recommendation"] or res[command]["suspicious"]:
            print(f'{command}:')
            for item in res[command]:
                if concise and item != "recommendation" and item != "suspicious":
                        continue
                if res[command][item]:
                    print(f'\t{item}:')
                    if type(res[command][item]) == list:
                        data = '\n\t\t'.join(json.dumps(i) for i in res[command][item])
                    else:
                        data = res[command][item]
                    print(f'\t\t{data}')


if __name__ == '__main__':

    TEST=True
    args = None
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sys_name', help='system name', required=True)
    parser.add_argument('-i', '--ip', help='The tested Mikrotik IP address')
    parser.add_argument('-l', '--log', default = None, help='logging file, default will be system name')
    parser.add_argument('-p', '--port', help='The tested Mikrotik SSH port', default='22')
    parser.add_argument('-u', '--userName', help='User name with admin Permissions', required=True)
    parser.add_argument('-ps', '--password', help='The password of the given user name', default='')
    parser.add_argument('-r','--region', help='region id', default='9')
    parser.add_argument('--mode', default='config', const='config',
                        nargs='?',
                        choices=['config', 'dump'],
                        help='configure (config) or dump (dump) device (default: %(default)s')
    parser.add_argument('--template', help='template file', default='./templates/ptp_config.json')
    parser.add_argument('--db', help='configuration db', default='./data/region9_hamwan.sqlite3')
    parser.add_argument('--dtype', default='PTP', const='PTP',
                        nargs='?',
                        choices=["PTP", "SECTOR", "Router"],
                        help='device type PTP, SECTOR, ROUTER (default: %(default)s')
    parser.add_argument('-c', '--check_dev', help='Check attached device system name and IP', action='store_true')
    parser.add_argument('-J', help='Print the results as json format', action='store_true')
    parser.add_argument('-concise', help='Print out only suspicious items and recommendations', action='store_true')
    parser.add_argument('-update', help='Update the CVE Json file', action='store_true')

    if TEST == True:
        args= parser.parse_args(['-s','SPODEM.PTP1','--port','22','-u','admin','-ps','SnoDEM720'])
    else:
        args = parser.parse_args()

    #print(args)

    main(args)

