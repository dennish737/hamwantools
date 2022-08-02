import os
import sys
import datetime
import sqlite3

from datetime import datetime
import pandas as pd
import numpy as np
import ipaddress
import logging
from libs.dbtools import DbSqlite
from libs.ip_tools import ip2long, ip2hex, int2ip, hex2ip

file = './data/spokane_example.sqlite3'


try:
    db = DbSqlite()
    db.connect(file)

    org_id = db.getOrganizationId('spokane')
    equipment_groups = db.getEquipmentGroups()
    print(equipment_groups)


except sqlite3.Error as error:
    print("Failed to read data from sqlite table", error)
finally:
    db.close()


