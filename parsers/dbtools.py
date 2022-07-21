import sqlite3
import pandas as pd
import numpy as np
import json
import logging

class DbSqlite():
    def __init__(self):
        self.db_file = None
        self.conn = None
        # add support for np int32 and  int64 used by pandas
        sqlite3.register_adapter(np.int64, lambda val: int(val))
        sqlite3.register_adapter(np.int32, lambda val: int(val))
        sqlite3.register_adapter(list, self._adaptListToJSON)
        sqlite3.register_converter("json", self._convertJSONToList)
        """ use JSON list storage, connect with detect_types=sqlite3.PARSE_DECLTYPES and declare 
            your column type as json, or use detect_types=sqlite3.PARSE_COLNAMES and use [json] 
            in a column alias (SELECT datacol AS "datacol [json]" FROM ...) to trigger the 
            conversion on loading."""

    def _adaptListToJSON(self, lst):
        return json.dumps(lst).encode('utf8')

    def _convertJSONToList(self, data):
        return json.loads(data.decode('utf8'))

    def close(self):
        self.db_file = None
        self.conn.close()
        self.conn = None

    def _connect(self):
        if self.conn is not None:
            self.close()

        try:
            conn = sqlite3.connect(self.db_file)
        except sqlite3.Error as e:
            logging.error(e)
        self.conn = conn

    def connect(self, db_file):
        if db_file is None:
            raise ValueException('requires a valid db_file name. None provided')

        if self.conn is not None:
            self.close()

        try:
            conn = sqlite3.connect(db_file)
        except sqlite3.Error as e:
            logging.error(e)
        self.conn = conn
        self.db_file = db_file

    def getTableColumnNames(self, table):
        query = 'PRAGMA table_info({})'.format(table)
        cursor = self.conn.execute('PRAGMA table_info(sites)')
        desc = cursor.fetchall()
        # getting names using list comprehension
        names = [fields[1] for fields in desc]
        cursor.close()
        return names

    def getQueryData(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        desc = cursor.description
        names = map(lambda x: x[0], desc)
        rows = cursor.fetchall()
        df = None
        if len(rows) > 0:
            df = pd.DataFrame(rows, columns=names)
        cursor.close()
        return df

    def getQueryDictionary(self, query):
        # This is the important part, here we are setting row_factory property of
        # connection object to sqlite3.Row(sqlite3.Row is an implementation of
        # row_factory)

        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute(query)

        result = [dict(row) for row in cursor.fetchall()]

        # returns a list of dictionaries, each item in list(each dictionary)
        # represents a row of the table
        cursor.close()
        return result

    def getAvailablePTPIps(self, org_id):
        # Available PTP IPs are those that have not been assigned to a block, and are not assigned
        query = """SELECT id, org_id, ip_address 
        FROM ip_addresses WHERE ip_type = (SELECT id FROM ip_types WHERE type_name = 'ptp') AND 
        reserved = 0 and assigned = 0 AND org_id = {}
        ORDER BY id;"""
        df = self.getQueryData(query.format(org_id))
        return df

    def getDefaultGateways(self, org_id):
        # default gateways are use for virtual routing setings. Each organization has
        # at least one default gateway. Users can define multiple default gateways
        # by defining multiple vrrp interfaces, each with a unique names. If you want multiple default
        # gateways (load balancing), you can simply increase the number of vrrp interfaces for
        # default_gateways in equipment_groups.

        # query to search the organizational space to find all default gateways and return the interface information
        query = """SELECT  if.id, if.equip_id, if.if_name, ip.id as ip_id, ip.ip_address
            FROM sites s
            INNER JOIN site_equipment se
            ON se.site_id = s.id
            INNER JOIN interfaces if
            ON if.equip_id = se.id
            LEFT OUTER JOIN ip_addresses ip
            ON ip.id = if.addr_id
            WHERE s.org_id = {0} AND 
            se.group_id = (SELECT y.id FROM equipment_groups y WHERE lower(y.group_name) = 'default_gateway');
            """
        df = self.getQueryData(query.format(org_id))
        return df

    def getDeviceIP(self, device_name):
        query = 'select etherip, device_type from routers where sys_name = ?;'
        cursor = self.conn.cursor()
        cursor.execute(query, (device_name,))

        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more thant one row returned for device={device_name}')

        ip_address = rows[0][0]
        router_type = rows[0][1]
        cursor.close()
        return ip_address, router_type

    def getDeviceName(self, ip):
        query = 'select sys_name, device_type from routers where etherip LIKE ?;'
        ip_like = f'%{ip}%'
        cursor = self.conn.cursor()
        cursor.execute(query, (ip_like,))

        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more thant one row returned for device={ip}')

        sys_name = rows[0][0]
        router_type = rows[0][1]
        return sys_name, router_type

    def getEquipmentGroup(self, name):
        query = 'select id, suffix from equipment_groups where lower(group_name) = ?;'
        cursor = self.conn.cursor()
        cursor.execute(query, (name.lower(),))

        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError('more than one row returned for site type={0}'.format(name))
        if len(rows) == 0:
            raise ValueError('site type={0} not found'.format(name))
        eqp_group_id = rows[0][0]
        eqp_suffix = rows[0][1]
        return (eqp_group_id, eqp_suffix)

    def getEquipmentId(self, org_id, name):
        query = 'SELECT id, name FROM site_equipment WHERE org_id = ? AND lower(name) = ?;'
        id = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (org_id, name.lower()))
            row = cursor.fetchone()
            id = row[0]
            eqp_name = row[1]
        except sqlite3.Error as error:
            logging.error("failed ot read equipment name with id = {}".format(id))
        return id, eqp_name

    def getEquipmentInfo(self, equip_id, if_type=None):
        query = """SELECT se.id as dev_id, se.name as dev_name, if.id as if_id, if.if_type as if_type, if.if_name as if_name, ip.ip_address as ip_address 
            FROM site_equipment se
            LEFT OUTER JOIN interfaces if
            ON if.equip_id = se.id
            LEFT OUTER JOIN ip_addresses ip
            ON ip.id = if.addr_id
            WHERE se.id = {0} """.format(equip_id)

        if if_type is not None:
            query = query + " AND lower(if.if_type) = '{0}';".format(if_type)
        else:
            query += ';'
        d = self.getQueryDictionary(query)
        return d

    def getEquipmentName(self, id):
        query = 'SELECT name FROM site_equipment WHERE id = ?;'
        name = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (id,))
            row = cursor.fetchone()
            name = row[0]
        except sqlite3.Error as error:
            logging.error("failed to read equipment name with id = {}".format(id))

        return name

    def getAllEquipment(self, org_name):
        query = """SELECT s.name as "site", se.id as "e_id", se.name as "device_name"
                FROM sites s
                INNER JOIN site_equipment se
                ON se.site_id = s.id
                WHERE s.org_id = (SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = {})"""
        df = self.getQueryData(query.format(org_name))
        return df

    def getSiteEquipment(self, org_id, site_name):
        query = """SELECT s.name as "site", se.id as "e_id", se.name as "device_name"
                FROM sites s
                INNER JOIN site_equipment se
                ON se.site_id = s.id
                WHERE irg_id = {0} AND s.id = (SELECT x.id FROM sites x WHERE lower(x.site_name) = {1})"""
        df = self.getQueryData(query.format(org_id, site_name))
        return df

    def getSiteAssignedInterfacesByType(self, site_id, if_type='all'):
        query_type = """SELECT  se.name as "equipment_name", if.if_type as "type" , if.if_name as "if_name"
            FROM site_equipment se
            INNER JOIN interfaces if
            ON if.equip_id = se.id
            WHERE se.site_id = {0} AND if_type = {1}"""
        query_all = """SELECT  se.name as "equipment_name", if.if_type as "type" , if.if_name as "if_name"
            FROM site_equipment se
            INNER JOIN interfaces if
            ON if.equip_id = se.id
            WHERE se.site_id = {0}"""

        df = None
        # think about moving adding interface table
        if if_type != 'all' and if_type not in ['ether', 'wlan', 'vrrp']:
            logging.error("type {} not a valid interface type".format(if_type))
            return df

        if if_type == 'all':
            df = self.getQueryData(query_all.format(site_id))
        else:
            df = self.getQueryData(query_type.format(site_id, if_type))
        pass

    def getOrgAssignedInterfacesByType(self, org_id, site_id=None, if_type='all'):

        query = """SELECT s.name as "site", se.name as "device_name", if.if_type as if_type, if.if_name as if_name
                        FROM sites s
                        INNER JOIN site_equipment se
                        ON se.site_id = s.id
                        INNER JOIN interfaces if
                        ON if.equip_id = se.id
                        WHERE s.org_id = {0}
                """
        if site_id is None:
            query = query.format(org_id)
        else:
            query = query.format(org_id) + ' AND se.id = {0}'.format(site_id)

        if (if_type != 'all'):
            query += " AND if.if_type = '{0}';".format(if_type)
        else:
            query += ';'

        df = self.getQueryData(query)
        return df

    def getSiteAvailableEquipmentInterfaces(self, org_id, site_id=None):
        query = """SELECT s.name as "site", se.id as "e_id", se.name as "device_name", sg.interface_list as ifaces
                FROM sites s
                INNER JOIN site_equipment se
                ON se.site_id = s.id
                INNER JOIN equipment_groups sg
                ON sg.id = se.group_id
                WHERE s.org_id = {0}
                """
        if site_id is None:
            query = query.format(org_id) + ';'
        else:
            query = query.format(org_id) + ' AND s.id = {0}'.format(site_id)

        df = self.getQueryData(query)
        new_data = []
        for idx, row in df.iterrows():
            if_list = json.loads(row['ifaces'])

            for key, values in if_list.items():
                for value in values:
                    new_row = {}
                    # copy everything except ifaces
                    for row_key, row_value in row.items():
                        if row_key != 'ifaces':
                            new_row[row_key] = row_value
                    new_row['if_type'] = key
                    new_row['if_name'] = value
                    new_data.append(new_row)
        df_new = pd.DataFrame(new_data)
        return df_new

    def gerFirstAvailableEtherIpAddress(self,org_id):
        query = """SELECT id, ip_address FROM ip_addresses WHERE org_id = ? AND assigned = 0 AND reserved = 0 AND
        ip_type = (SELECT x.id FROM ip_types x WHERE lower(type_name) = 'device' )
		ORDER BY id LIMIT 1;"""
        cursor = self.conn.cursor()
        cursor.execute(query, (org_id,))
        result = cursor.fetchone()
        id = None
        ip_addr = None
        if result:
            ip_id = result[0]
            ip_addr = result[1]
        cursor.close()
        return ip_id, ip_addr

    def assignEtherIpAddress(self, if_id, ip_addr_id):
        logging.debug("assignEtherIpAddress, if_if = {0}, ip_addr_id= {1}".format(if_id, ip_addr_id))
        query1 = "UPDATE interfaces SET addr_id = ?, new = 0 WHERE  id = ?;"
        query2 = "UPDATE ip_addresses SET assigned = ? WHERE id = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query1, (ip_addr_id, if_id))
        cursor.execute(query2, (if_id, ip_addr_id))
        self.conn.commit()
        cursor.close()

    def linkEtherIpAddress(self, if_id, ip_addr_id):
        logging.debug("linkEtherIpAddress, if_if = {0}, ip_addr_id= {1}".format(if_id, ip_addr_id))
        query = "UPDATE interfaces SET addr_id = ?, new = 0 WHERE  id = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (ip_addr_id, if_id))
        self.conn.commit()
        cursor.close()

    def getFirstAvailablePTP(self, site):
        query = """SELECT id, name FROM site_equipment WHERE site_id = ? AND 
                active = 0 AND
                group_id=(SELECT y.id FROM equipment_groups y WHERE y.suffix = 'PTP')
                ;"""
        cursor = self.conn.cursor()
        cursor.execute(query, (site,))

        # get the first one
        row = cursor.fetchone()
        cursor.close()
        return row[0], row[1]

    def getFirstAvailablePTPBlock(self, org_id):
        query = "SELECT id, ip_a, ip_b FROM ptp_blocks WHERE assigned is NULL AND org_id = {0} ORDER BY id LIMIT 1;".format(org_id)
        block = self.getQueryDictionary(query)[0]
        return block

    def getPTPBlock(self, block_id):
        query = "SELECT id, ip_a, ip_b FROM ptp_blocks WHERE id = {0} LIMIT 1;".format(block_id)
        block = self.getQueryDictionary(query)[0]
        return block

    def assignPTPBlockToPath(self, path_id, ptp_block_id):
        query1 = "UPDATE ptp_blocks SET assigned = ? WHERE id = ?;"
        query2 = "UPDATE paths SET ptp_block = ? WHERE id = ?;"

        cursor = self.conn.cursor()
        cursor.execute(query1, (path_id, ptp_block_id))
        cursor.execute(query2, (ptp_block_id, path_id))


    def getIPTypes(self):
        query = 'SELECT * FROM ip_types ORDER BY id'
        self.conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        d = {}
        for row in results:
            d[row['type_name']] = row['id']
        cursor.close()
        return d

    def getNewAddressBlocks(self, org_id):
        query = 'SELECT id, org_id, network, broadcast FROM address_blocks WHERE new = 1 AND org_id = {};'
        df = self.getQueryData(query.format(org_id))
        return df

    def getNewPTPBlocks(self, org_id):
        query = 'SELECT id, org_id, ip_a, ip_b FROM ptp_blocks WHERE new = 1 AND org_id = {};'
        df = self.getQueryData(query.format(org_id))
        return df

    def getOrganizationData(self, org_id):
        query = 'select * from organizations where org_id = ?;'
        org_params = {}

        cursor = self.conn.cursor()
        cursor.execute(query, (org_id,))

        col_names = list(map(lambda x: x[0], cursor.description))

        row = cursor.fetchone()

        for i in range(len(col_names)):
            org_params[col_names[i]] = row[i]
        cursor.close()
        return org_params

    def getOrganizationId(self, name):
        query = 'select org_id from organizations where lower(club_name) = ?;'
        cursor = self.conn.cursor()
        cursor.execute(query, (name.lower(),))

        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more thant one row returned for device={device_name}')
        org_id = rows[0][0]
        cursor.close()
        return org_id

    def getOrgPaths(self, org_id):
        query = "SELECT * FROM paths WHERE org_id = {}"
        results = self.getQueryData(query.format(org_id))
        return results

    def getPathType(self, name):
        query = "select id from path_types where identifier = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (name,))

        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more than one row returned for site type={name}')
        path_type_id = rows[0][0]
        return path_type_id

    def getPoolAddresses(self, org_id):
        query = """SELECT id, org_id, ip_address FROM ip_addresses 
            WHERE ip_type = (select id from ip_types where type_name = "pool" AND reserved = 0 and org_id = {0});"""
        df = self.getQueryData(query.format(org_id))
        return df


    def getSiteType(self, name):
        query = 'select id from site_types where description = ?;'
        cursor = self.conn.cursor()
        cursor.execute(query, (name.lower(),))

        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more than one row returned for site type={name}')
        site_type_id = rows[0][0]
        cursor.close()
        return site_type_id

    def getSiteId(self, org_id, name):
        query = 'SELECT id FROM sites WHERE lower(name) = ? and org_id = ?;'
        cursor = self.conn.cursor()
        cursor.execute(query, (name.lower(),org_id))
        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more than one row returned for site={name}')
        site_id = rows[0][0]
        cursor.close()
        return site_id

    def getSiteEquipmentCounts(self, site_id):
        query = 'SELECT num_routers, num_sectors, num_ptp from sites WHERE id = ?'
        cursor = self.conn.cursor()
        cursor.execute(query, (site_id,))
        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more than one row returned for site={site_id}')
        num_routers = rows[0][0]
        num_sectors = rows[0][1]
        num_ptp = rows[0][2]
        return num_routers, num_sectors, num_ptp

    def updateSiteRouterCount(self, site_id, value):
        query = 'UPDATE sites SET num_routers = ? WHERE id = ?;'
        cursor = self.conn.cursor()
        cursor.execute(query, (value,site_id,))
        self.conn.commit()

    def updateSiteSectorCount(self, site_id, value):
        query = 'UPDATE sites SET num_sectors = ? WHERE id = ?;'
        cursor = self.conn.cursor()
        cursor.execute(query, (value,site_id,))
        self.conn.commit()

    def updateSitePTPCount(self, site_id, value):
        query = 'UPDATE sites SET num_ptp = ? WHERE id = ?;'
        cursor = self.conn.cursor()
        cursor.execute(query, (value,site_id,))
        self.conn.commit()

    def assignEquipmentToPTPPath(self, path_id, device_a_id, device_b_id):
        # make sure we have everything

        # paths are point to point
        try:
            update_path = 'UPDATE paths SET device_a = ?, device_b = ? WHERE id = ?;'
            update_equipment ='UPDATE site_equipment SET active = 1 WHERE id = ?;'
            cursor = self.conn.cursor()
            cursor.execute(update_path, (device_a_id, device_b_id, path_id,))
            cursor.execute(update_equipment,(device_a_id,))
            cursor.execute(update_equipment, (device_b_id,))
            self.conn.commit()
        except sqlite3.Error as error:
            logging.error("assignedEquipmentToPTPPath failed path_id={0}, device_a_id={1}, device_b_id={2}",
                  path_id, device_a_id, device_b_id)


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

        cursor = self.conn.cursor()
        cursor.execute(query, (region,))

        rows = cursor.fetchall()

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

        cursor = self.conn.cursor()
        cursor.execute(query, (sys_name,))

        rows = cursor.fetchall()

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
