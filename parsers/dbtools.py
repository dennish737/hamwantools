import sqlite3
import pandas as pd

class DbSqlite():
    def __init__(self):
        self.db_file = None
        self.conn = None

    def close(self):
        self.db_file = None
        self.conn.close()
        self.conn = None

    def _connect(self):
        if self.conn is not None:
            self.close()

        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        self.conn = conn

    def connect(self, db_file):
        if db_file is None:
            raise ValueException('requires a valid db_file name. None provided')

        if self.conn is not None:
            self.close()

        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        self.conn = conn
        self.db_file = db_file

    def getTableColumnNames(self, table):
        query = 'PRAGMA table_info({})'.format(table)
        cursor = self.conn.execute('PRAGMA table_info(sites)')
        desc = cursor.fetchall()
        # getting names using list comprehension
        names = [fields[1] for fields in desc]
        return names

    def getQueryData(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        desc = cursor.description
        names = map(lambda x: x[0], desc)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=names)
        return df

    def getDeviceIP(self, device_name):
        query = 'select etherip, device_type from routers where sys_name = ?;'
        cur = self.conn.cursor()
        cur.execute(query, (device_name,))

        rows = cur.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more thant one row returned for device={device_name}')

        ip_address = rows[0][0]
        router_type = rows[0][1]
        return ip_address, router_type

    def getOrganizationId(self, name):
        query = 'select org_id from organizations where club_name = ?;'
        cur = self.conn.cursor()
        cur.execute(query, (name,))

        rows = cur.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more thant one row returned for device={device_name}')
        org_id = rows[0][0]
        return org_id

    def getOrganizationData(self, org_id):
        query = 'select * from organizations where org_id = ?;'
        org_params = {}

        cur = self.conn.cursor()
        cur.execute(query, (org_id,))

        col_names = list(map(lambda x: x[0], cur.description))

        row = cur.fetchone()

        for i in range(len(col_names)):
            org_params[col_names[i]] = row[i]
        return org_params

    def getSiteType(self, name):
        query = 'select id from site_types where description = ?;'
        cur = self.conn.cursor()
        cur.execute(query, (name.lower(),))

        rows = cur.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more than one row returned for site type={name}')
        site_type_id = rows[0][0]
        return site_type_id

    def getEquipmentType(self, name):
        query = 'select id from equipment_types where description = ?;'
        cur = self.conn.cursor()
        cur.execute(query, (name.lower(),))

        rows = cur.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more than one row returned for site type={name}')
        eqp_type_id = rows[0][0]
        return eqp_type_id

    def getPathType(self, name):
        query = "select id from path_types where identifier = ?;"
        cur = self.conn.cursor()
        cur.execute(query, (name,))

        rows = cur.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more than one row returned for site type={name}')
        path_type_id = rows[0][0]
        return path_type_id

    def getDeviceName(self, ip):
        query = 'select sys_name, device_type from routers where etherip LIKE ?;'
        ip_like = f'%{ip}%'
        cur = self.conn.cursor()
        cur.execute(query, (ip_like,))

        rows = cur.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more thant one row returned for device={ip}')

        sys_name = rows[0][0]
        router_type = rows[0][1]
        return sys_name, router_type

    def getRegionInfo(self, region):
        columns = ['network_allocation',
                   'wirelessname', 'wirelesskey',
                   'backbonename', 'backbonekey',
                   'defaultgateway', 'vrrpkey',
                   'ospfkey',
                   'log_server',
                   'dns_server1',
                   'dns_server2',
                   'ntp_server1',
                   'ntp_server2',
                   'timezone']

        query = "select " + ",".join(columns) + " from regions where regionid = ?;"

        cur = self.conn.cursor()
        cur.execute(query, (region,))

        rows = cur.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more thant one row returned for region={region}')

        region_params = {}
        row = rows[0]
        for i in range(len(row)):
            # build a dictionary of parameters
            region_params[columns[i]] = row[i]

        return region_params

    def getPTPParams(self, sys_name):
        columns = ['sys_name', '_from', '_to', 'routername', 'wlan1_ip',
                   'netaddress', 'ether1_ip', 'remote_routername', 'remoteip']

        query= """select a.sys_name, a._from, a._to, a.routername, a.wanip, a.netaddress, c.etherip,b.routername, 
                b.wanip 
                from ptprouters a
                inner join ptprouters b
                on b._to = a._from and b._from = a._to
                inner join routers c
                on c.sys_name = a.sys_name
                where a.sys_name = ?;
                """

        cur = self.conn.cursor()
        cur.execute(query, (sys_name,))

        rows = cur.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more thant one row returned for ptp router={sys_name}')

        ptp_params = {}

        row = rows[0]
        
        for i in range(len(row)):
            # build a dictionary of parameters
            ptp_params[columns[i]] = row[i]

        return ptp_params




if __name__ == '__main__':
    # used for testing
    db_file = "../data/region9_hamwan.sqlite3"
    operation = 'config'
    device_name = "SPODEM.PTP1"
    region = 9

    db = DbSqlite()
    db.connect(db_file)
    ip, device_type = db.getDeviceIP(device_name)
    print(device_name, ip, device_type)
    print("------------")
    ip2 = "44.12.135.16"
    sys_name, d_type = db.getDeviceName(ip2)
    print(ip2, sys_name, d_type)
    print("------------")
    region_params = db.getRegionInfo(region)
    print("------------")
    print(region_params)
    print("------------")
    if device_type == 'PTP':
        ptp_params = db.getPTPParams(device_name)
        print(ptp_params)
