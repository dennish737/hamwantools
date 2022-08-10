import sqlite3
import pandas as pd
import numpy as np
import json
import logging
import ipaddress

# some useful ip function for sqlite
# convert ip address to long int

def _ip2long(ip_addr):
    return int(ipaddress.ip_address(ip_addr))

# Convert IP address to hex integer

def _ip2hex(ip_addr):
    return hex(int(ipaddress.ip_address(ip_addr)))


# convert long integer to hex

def _int2ip(i):
    return str(ipaddress.ip_address(i))

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

    # some useful ip function for sqlite
    # convert ip address to long int

    def close(self):
        self.db_file = None
        self.conn.close()
        self.conn = None

    def _connect(self):
        if self.conn is not None:
            self.close()

        try:
            connection = sqlite3.connect(self.db_file)
            self.conn = connection
        except sqlite3.Error as e:
            logging.error(e)


    def connect(self, file):
        if file is None:
            raise ValueError('requires a valid db_file name. None provided')

        if self.conn is not None:
            self.close()

        try:
            conn = sqlite3.connect(file)
            self.conn = conn
            self.db_file = file
        except sqlite3.Error as e:
            logging.error(e)


    def _clearTable(self, table_name):
        query1 = "DELETE FROM ?;"
        query2 = "UPDATE sqlite_sequence SET seq=0 WHERE name = '?';"
        cursor = self.conn.cursor()
        cursor.execute(query1, (table_name,))
        cursor.execute(query2, (table_name,))
        self.conn.commit()
        cursor.close()

    def getTableColumnNames(self, table):
        query = 'PRAGMA table_info({})'.format(table)
        cursor = self.conn.execute(query)
        desc = cursor.fetchall()
        # getting names using list comprehension
        names = [fields[1] for fields in desc]
        cursor.close()
        return names

    def getQueryData(self, query, *args):
        cursor = self.conn.cursor()
        cursor.execute(query, args)
        desc = cursor.description
        names = map(lambda x: x[0], desc)
        rows = cursor.fetchall()
        df = None
        if len(rows) > 0:
            df = pd.DataFrame(rows, columns=names)
        cursor.close()
        return df

    def getQueryDictionary(self, query, *args):
        # This is the important part, here we are setting row_factory property of
        # connection object to sqlite3.Row(sqlite3.Row is an implementation of
        # row_factory)

        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute(query, args)

        result = [dict(row) for row in cursor.fetchall()]

        # returns a list of dictionaries, each item in list(each dictionary)
        # represents a row of the table
        cursor.close()
        return result

    def getSingleRowQueryDictionary(self, query, *args):
        result = None
        try:
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            row = cursor.fetchone()
            if row:
                result = dict(row)
            cursor.close()
        except sqlite3.Error as error:
            logging.error(error)
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

    def getSitesEquipmentCount(self, site_id):
        query = "SELECT num_routers, num_sectors, num_ptp FROM sites WHERE id = ?;"
        cursor = self.conn.cursor()
        cursor.row_factory = lambda cursor, row: (row[0], row[1], row[2])
        cursor.execute(query, (site_id,))
        results = cursor.fetchall()
        cursor.close()
        return results

    def getEquipmentGroups(self):
        query = "SELECT group_name, id FROM equipment_groups;"
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        results = {}
        for row in rows:
            results[row[0]] = row[1]
        cursor.close()
        return results

    def getEquipmentGroup(self, name):
        query = 'select id, suffix from equipment_groups where lower(group_name) = ?;'
        cursor = self.conn.cursor()
        cursor.execute(query, (name.lower(),))

        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more than one row returned for site type={name}')
        elif len(rows) < 1:
            # nothing was returned
            raise ValueError(f' type={name}, not valid. Check input file')

        eqp_group_id = rows[0][0]
        eqp_suffix = rows[0][1]
        return (eqp_group_id, eqp_suffix)

    def getEquipmentId(self, org_id, name):
        query = 'SELECT id, name FROM site_equipment WHERE org_id = ? AND lower(name) = ?;'
        id = None
        eqp_name = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (org_id, name.lower()))
            row = cursor.fetchone()
            id = row[0]
            eqp_name = row[1]
        except sqlite3.Error as error:
            logging.error("failed to read equipment name with id = {}".format(id))
        return id, eqp_name

    def _getEquipmentInfo(self, equip_id):
        query = """SELECT se.name as device_name, se.group_id, if_type, if_name, if.addr_id, if.dhcp_id 
            FROM site_equipment se
            INNER JOIN interfaces if
            ON if.equip_id = se.id
            WHERE se.id = ?;"""

        equip_dict = self.getQueryDictionary(query, equip_id)
        return equip_dict

    def _getInterfaceIp(self, ip_id):
        query = """SELECT ip_type, ip_address, reserved FROM ip_addresses 
                WHERE id = ?;"""
        ip_address = None
        ip_type = None
        cidr = '/32'
        result = self.getSingleRowQueryDictionary(query,ip_id)
        if result is None:
            logging.error("failed to read ip_address of id = {}".format(ip_id))
        else:
            ip_address = result['ip_address']
            if result['ip_type'] == 1:
                cidr = '/27'
            elif result['ip_type'] == 2:
                cidr = '/31'
            else:
                cidr = '/32'
            if len(ip_address.split('/')) == 1:
                ip_address += cidr
            else:
                ip_address = ip_address.split('/')[0] + cidr
        return ip_address

    def _getInterfaceNetwork(self, ip_id):
        # the location of hte network address for an interface is dependent on the
        # type of interface
        query = """SELECT ip_type, reserved FROM ip_addresses 
                WHERE id = ?;"""
        ip_type = None
        ip_reserved = None
        network_ip = None
        dict1 = self.getSingleRowQueryDictionary(query, ip_id)
        if dict1:
            ip_type = dict1['ip_type']
            ip_reserved = dict1['reserved']
            if ip_type == 1:    # address block
                query = "SELECT ip_address as network_ip FROM ip_addresses WHERE id = (SELECT x.network FROM address_blocks x WHERE x.id = ?);"
                dict2 = self.getSingleRowQueryDictionary(query, ip_reserved)
                if dict2:
                    network_ip = dict2['network_ip']
            elif ip_type == 2:  # ptp type
                query = """SELECT ptp.ip_a, ptp.ip_b, a.ip_address as ip_addr_a, b.ip_address as ip_addr_b FROM ptp_blocks ptp
                            INNER JOIN ip_addresses a
                            ON a.id = ptp.ip_a
                            INNER JOIN ip_addresses b
                            ON b.id = ptp.ip_b                            
                            WHERE ptp.id = ?;"""
                dict2 = self.getSingleRowQueryDictionary(query, ip_reserved)
                if dict2:
                    if ip_id == dict2['ip_a']:
                        network_ip = dict2['ip_addr_b']
                    else:
                        network_ip = dict2['ip_addr_a']
            elif ip_type == 3:  # router ip
                query = " SELECT ip_address FROM ip_addresses WHERE ip_type = 3 ORDER BY id LIMIT 1;"
                dict2 = self.getSingleRowQueryDictionary(query)
                if dict2:
                    network_ip = dict2['ip_address']
            else:
                logging.error("invalid ip_type {0} for ip_address {1}".format(ip_type, ip_id))
                raise ValueError("invalid ip_type {0} for ip_address {1}".format(ip_type, ip_id))
        else:
            logging.error("failed to read ip_address of network = {}".format(ip_reserved))
        if network_ip is not None:
            network_ip = network_ip.split('/')[0]
        return network_ip

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

    def getListOfSiteEquipmentIds(self,  site_id):
        query = "SELECT group_id, id as device_id, name as device_name FROM site_equipment WHERE site_id = ?"
        cursor = self.conn.cursor()
        cursor.row_factory = lambda cursor, row: (row[0], row[1], row[2])
        cursor.execute(query, (site_id,))
        results = cursor.fetchall()
        cursor.close()
        return results

    def getListOfAllSiteIds(self, org_id):
        query = "SELECT id FROM sites WHERE org_id = ? ORDER BY ID"
        cursor = self.conn.cursor()
        cursor.row_factory = lambda cursor, row: row[0]
        cursor.execute(query, (org_id,))
        results = cursor.fetchall()
        cursor.close()
        return results

    def getListOfAllSiteNames(self, org_id):
        query = "SELECT name FROM sites WHERE org_id = ? ORDER BY id"
        cursor = self.conn.cursor()
        cursor.row_factory = lambda cursor, row: row[0]
        cursor.execute(query, (org_id,))
        results = cursor.fetchall()
        cursor.close()
        return results

    def getSiteEquipment(self, org_id, site_name):
        query = """SELECT s.name as "site", se.id as "e_id", se.name as "device_name"
                FROM sites s
                INNER JOIN site_equipment se
                ON se.site_id = s.id
                WHERE org_id = {0} AND s.id = (SELECT x.id FROM sites x WHERE lower(x.site_name) = {1})"""
        df = self.getQueryData(query.format(org_id, site_name))
        return df

    def getSiteEquipmentById(self, site_id):
        query = """SELECT se.id as "id", se.group_id, se.name as "device_name"
                    FROM site_equipment se
                    WHERE se.site_id = ?
                    ORDER BY se.id;
                """
        df = self.getQueryData(query, site_id)
        return df

    def getSiteEquipmentByIdAndType(self, site_id, equip_type):
        query = """SELECT se.id as "id", se.group_id, se.name as "device_name"
                    FROM site_equipment se
                    WHERE se.site_id = ? AND se.group_id = ?
                    ORDER BY se.id;
                """
        df = self.getQueryData(query, site_id, equip_type)
        return df

    def getEquipmentInterfaces(self, equip_id, ift):
        query = "SELECT * FROM interfaces WHERE if_type = ? and equip_id = ?;"
        results = self.getQueryDictionary(query, ift, equip_id)
        return results

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
        query = """SELECT s.name as "site", se.id as "e_id", se.name as "device_name", sg.interface_list as iface
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
            if_list = json.loads(row['iface'])

            for key, values in if_list.items():
                for value in values:
                    new_row = {}
                    # copy everything except iface
                    for row_key, row_value in row.items():
                        if row_key != 'iface':
                            new_row[row_key] = row_value
                    new_row['if_type'] = key
                    new_row['if_name'] = value
                    new_data.append(new_row)
        df_new = pd.DataFrame(new_data)
        return df_new

    def getFirstAvailableRouterIfAddress(self, org_id):
        query = """SELECT id, ip_address FROM ip_addresses WHERE org_id = ? AND assigned = 0 AND reserved = 0 AND
        ip_type = (SELECT x.id FROM ip_types x WHERE lower(type_name) = 'device' )
		ORDER BY id LIMIT 1;"""
        cursor = self.conn.cursor()
        cursor.execute(query, (org_id,))
        result = cursor.fetchone()
        ip_id = None
        ip_addr = None
        if result:
            ip_id = result[0]
            ip_addr = result[1]
        cursor.close()
        return ip_id, ip_addr

    def getFirstAvailablePTP(self, site):
        query = """SELECT id, name FROM site_equipment WHERE site_id = ? AND 
                active = 0 AND
                group_id=(SELECT y.id FROM equipment_groups y WHERE y.group_name = 'bptp')
                ;"""
        cursor = self.conn.cursor()
        cursor.execute(query, (site,))

        # get the first one
        row = cursor.fetchone()
        cursor.close()
        return (row[0], row[1])

    def getFirstAvailablePTPBlock(self, org_id):
        query = "SELECT id, ip_a, ip_b FROM ptp_blocks WHERE assigned = 0 AND org_id = ? ORDER BY id LIMIT 1;"
        block = None
        blocks = self.getQueryDictionary(query, org_id)
        if len(blocks) > 0:
            block = blocks[0]
        return block

    def getFirstAvailableAddressBlock(self, org_id):
        query = "SELECT id, network,start_ip, end_ip, broadcast FROM address_blocks WHERE reserved" \
                " = 0 AND org_id = ? ORDER BY id LIMIT 1;"
        blocks = self.getQueryDictionary(query, org_id)
        block = None
        if len(blocks) > 0:
            block = blocks[0]
        return block

    def getFirstAvailableIPFromBlock(self, block_id):
        logging.debug("getFirstAvailableIPFromBlock started block_id = {0}".format(block_id))
        query = """SELECT id, ip_address FROM ip_addresses
            WHERE id > (SELECT x.network FROM address_blocks x WHERE x.id = ?) AND
            id < (SELECT y.broadcast FROM address_blocks y WHERE y.id = ?) AND assigned = 0
            ORDER BY id LIMIT 1;
        """

        ip_id = None
        ip_addr = None
        cursor = self.conn.cursor()
        cursor.execute(query, (block_id, block_id))
        row = cursor.fetchone()

        if row and len(row) > 0:
            ip_id = row[0]
            ip_addr = row[1]
        cursor.close()
        return (ip_id, ip_addr)

    def getLastAvailableIPFromBlock(self, block_id):
        logging.debug("getLastAvailableIPFromBlock started block_id= {0}".format(block_id))
        query = """SELECT id, ip_address FROM ip_addresses
            WHERE id = (select x.end_ip from address_blocks x where x.id = ?)
            AND assigned = 0 ORDER BY id LIMIT 1
        """
        ip_id = None
        ip_addr = None
        cursor = self.conn.cursor()
        cursor.execute(query, (block_id,))
        row = cursor.fetchone()

        if row and len(row) > 0:
            ip_id = row[0]
            ip_addr = row[1]
        cursor.close()
        return (ip_id, ip_addr)

    def getNetworkIPFromBlock(self, block_id):
        logging.debug("getNetworkIPFromBlock started block_id = {0}".format(block_id))
        query = "SELECT id, ip_address FROM ip_addresses WHERE id = (select x.network from address_blocks x where x.id = ?)"
        ip_id = None
        ip_addr = None
        cursor = self.conn.cursor()
        cursor.execute(query, (block_id,))
        row = cursor.fetchone()

        if row and len(row) > 0:
            ip_id = row[0]
            ip_addr = row[1]
        cursor.close()
        return (ip_id, ip_addr)

    def getBroadcastIPFromBlock(self, block_id):
        logging.debug("getBroadCastIPFromBlock started block_id = {0}".format(block_id))
        query = "SELECT id, ip_address FROM ip_addresses WHERE id = (select x.broadcast from address_blocks x where x.id = ?)"
        ip_id = None
        ip_addr = None
        cursor = self.conn.cursor()
        cursor.execute(query, (block_id,))
        row = cursor.fetchone()

        if row and len(row) > 0:
            ip_id = row[0]
            ip_addr = row[1]
        cursor.close()
        return (ip_id, ip_addr)

    def reserveAddressBlock(self, equip_id , block_id):
        logging.debug("reserveAddressBlock, device_id = {0}, block_id = {1}".format(equip_id, block_id))
        query1 = "UPDATE address_blocks SET reserved= ? WHERE id = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query1, (equip_id, block_id))
        self.conn.commit()
        cursor.close()

    def assignInterfaceIPAddress(self, if_id, ip_addr_id):
        logging.debug("assignInterfaceIpAddress, if_if = {0}, ip_addr_id= {1}".format(if_id, ip_addr_id))
        query1 = "UPDATE interfaces SET addr_id = ?, new = 0 WHERE  id = ?;"
        query2 = "UPDATE ip_addresses SET assigned = ? WHERE id = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query1, (ip_addr_id, if_id))
        cursor.execute(query2, (if_id, ip_addr_id))
        self.conn.commit()
        cursor.close()

    def assignAddressBlock(self, equip_id, block_id):
        logging.debug("assigningAddressBlock, equip_id = {0}, block_id = {1}".format(equip_id, block_id))
        query = "UPDATE address_blocks SET assigned = ? WHERE id = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (equip_id, block_id))
        self.conn.commit()
        cursor.close()

    def createDHCPBlock(self, org_id, if_id, pool_name, network, lower_addr, upper_addr, gateway_addr, dns_addr=None):
        logging.debug("assignDHCPBlock, if_id = {0},  pool_name = {1}".format(if_id, pool_name))
        query1 = """INSERT OR IGNORE INTO dhcp_pools (org_id, if_id, pool_name, network, lower_addr, upper_addr, gateway_addr, dns_addr)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
        query2 = 'SELECT seq FROM sqlite_sequence where name="dhcp_pools"'
        cursor = self.conn.cursor()
        cursor.execute(query1, (org_id, if_id, pool_name, network, lower_addr, upper_addr, gateway_addr, dns_addr))
        self.conn.commit()
        cursor.close()
        # get id from last row entered
        cursor = self.conn.cursor()
        cursor.execute(query2)
        dhcp_id, = cursor.fetchone()
        cursor.close()
        query3 = "UPDATE interfaces SET dhcp_id = ?, new = 0 WHERE  id = ?;"
        query4 = "UPDATE ip_addresses SET assigned = ? WHERE id >= ? AND id <= ?;"
        cursor = self.conn.cursor()
        cursor.execute(query3, (dhcp_id, if_id))
        cursor.execute(query4, (if_id, lower_addr, upper_addr))
        self.conn.commit()
        cursor.close()
        return dhcp_id

    def linkEtherIpAddress(self, if_id, ip_addr_id):
        logging.debug("linkEtherIpAddress, if_if = {0}, ip_addr_id= {1}".format(if_id, ip_addr_id))
        query = "UPDATE interfaces SET addr_id = ?, new = 0 WHERE  id = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (ip_addr_id, if_id))
        self.conn.commit()
        cursor.close()

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
        self.conn.commit()
        cursor.close()

    def getIPTypes(self):
        query = 'SELECT * FROM ip_types ORDER BY id'
        self.conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        d = {}
        for row in results:
            d[row['type_name']] = row['id']
        self.conn.row_factory = None
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
        query = "select org_id FROM organizations WHERE lower(club_name) = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (name.lower(),))

        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more thant one row returned for device={name}')
        org_id = rows[0][0]
        cursor.close()
        return org_id

    def getOrgPaths(self, org_id):
        query = "SELECT * FROM paths WHERE org_id = {}"
        results = self.getQueryData(query.format(org_id))
        return results

    def getListOfPathIds(self, org_id, path_type):
        query = """SELECT id FROM paths WHERE org_id = ?  
                AND type_id = (SELECT x.id FROM path_types x WHERE lower(description) = ?) ORDER BY ID"""
        cursor = self.conn.cursor()
        cursor.row_factory = lambda cursor, row: row[0]
        cursor.execute(query, (org_id, path_type))
        results = cursor.fetchall()
        cursor.close()
        return results

    def getPathId(self, org_id, path_name, path_type):
        query = """SELECT id FROM paths WHERE lower(name) = ? and org_id = ?
            AND type_id = (SELECT x.id FROM path_types x WHERE lower(description) = ?);"""
        cursor = self.conn.cursor()
        cursor.execute(query, (path_name.lower(),org_id, path_type))
        rows = cursor.fetchall()

        # we expect only one row to be returned
        if len(rows) > 1:
            raise ValueError(f'more than one row returned for path={path_name}')
        path_id = rows[0][0]
        cursor.close()
        return path_id

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

    def getSiteRouterAddressBlock(self, site_id):
        query = """SELECT * FROM address_blocks 
                WHERE reserved = (SELECT se.id FROM site_equipment se WHERE se.site_id = ? AND
                se.group_id = (SELECT eg.id FROM equipment_groups eg WHERE eg.group_name = 'router'));"""
        results = self.getQueryDictionary(query,site_id)
        return results

    def getSiteDeviceAddressBlock(self, device_id):
        query = "SELECT * FROM address_blocks WHERE reserved = ? ORDER BY id LIMIT 1"
        results = self.getQueryDictionary(query,device_id)
        return results


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

    def _getOrgParameters(self, org_id):
        query = "SELECT call_sign, club_contact FROM organizations WHERE org_id = ?;"
        results = self.getQueryDictionary(query, org_id)
        return results

    def _getOrgGlobalParameters(self, org_id):
        query = "SELECT timezone, log1, log2, dns1, dns2, ntp1, ntp2 FROM global_parameters WHERE org_id = ? and site_id is NULL;"
        results = self.getQueryDictionary(query, org_id)
        return results

    def _getSiteGlobalParameters(self, org_id, site_id):
        query = "SELECT timezone, log1, log2, dns1, dns2, ntp1, ntp2 FROM global_parameters WHERE org_id = ? and site_id = ?;"
        results = self.getQueryDictionary(query, org_id, site_id)
        return results

    def getGlobalParameters(self, org_id, site_id):
        org_params = self._getOrgParameters(org_id)
        global_org_params = self._getOrgGlobalParameters(org_id)
        global_site_params = self._getSiteGlobalParameters(org_id, site_id)

        results = None
        if len(org_params) > 0:
            print(org_params)
            results = org_params[0]
        else:
            results = {'call_sign': None, 'club_contact': None}

        # merge in site global params
        if len(global_site_params) > 0:
            for k,v in global_site_params[0].items():
                results[k] = v

        if len(global_org_params) > 0:
            # check for missing values
            for k, v in global_org_params[0].items():
                if k in results.keys():
                    v1 = results[k]
                    results[k] = v1 if v1 is not None else v
                else:
                    results[k] = v

        # add missing items
        key_list = ["timezone", "log1", "log2", "dns1", "dns2", "ntp1", "ntp2"]
        for key in key_list:
            if key not in results.keys():
                results[key] = None

        # add ptp security parameters
        return results


    def _getOrgPTPSecurity(self, org_id):
        query = "SELECT ssid as ptp_ssid, passwd as password FROM ptp_security WHERE org_id = ? AND path_id is NULL ORDER BY id;"
        results = self.getQueryDictionary(query, org_id)
        print("_getOrgPTPSecurity: results = ", results)
        return results

    def _getSitePTPSecurity(self, org_id, path_id):
        query = "SELECT ssid as ptp_ssid, passwd as password FROM ptp_security WHERE org_id = ? AND path_id = ? ORDER BY id;"
        results = self.getQueryDictionary(query, org_id, path_id)
        print("_getSitePTPSecurity: results = ", results)
        return results



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

    def _getPathName(self, ip_id, device_id):
        query = """SELECT ip_type, reserved FROM ip_addresses 
                WHERE id = ?;"""
        ip_type = None
        sys_name = None
        from_name = None
        to_name = None
        dict1 = self.getSingleRowQueryDictionary(query, ip_id)
        if dict1:
            ip_type = dict1['ip_type']
            ip_reserved = dict1['reserved']
            if ip_type == 2:
                query1 = """SELECT a.name as a_name, b.name as b_name, p.device_a, p.device_b
                            FROM paths p
                            INNER JOIN sites a
                            ON a.id = p.site_a
                            INNER JOIN sites b
                            ON b.id = p.site_b
                            WHERE p.id = (SELECT assigned from ptp_blocks where id = ?)"""
                paths = self.getSingleRowQueryDictionary(query1, ip_reserved)
                if paths['device_a'] == device_id:
                    sys_name = '.'.join([paths['b_name'] , paths['a_name']])
                    from_name = paths['a_name']
                    to_name = paths['b_name']
                else:
                    sys_name = '.'.join([paths['a_name'], paths['b_name']])
                    from_name = paths['b_name']
                    to_name = paths['a_name']
        return from_name, to_name, sys_name

    def getPTPParams(self, info, device_id, club_callsign):
        ptp_params = {}
        #
        count = 0
        for iface in info:
            if count == 0:
                count = 1
                ptp_params['sys_name'] = iface['device_name']
            if iface['addr_id'] is not None:
                ifname = iface['if_name'] + '_ip'
                ptp_params[ifname] = self._getInterfaceIp(iface['addr_id'])
                if iface['if_type'] == 'wlan':
                    ptp_params["remoteip"] = self._getInterfaceNetwork(iface['addr_id'])
                    ptp_params['_from'], ptp_params['_to'], ptp_params['radioname'] = self._getPathName(iface['addr_id'], device_id)
                    ptp_params['remote_routername'] = ptp_params['_from'] + '.' + ptp_params['_to']
                    ptp_params['sys_name'] = ptp_params['radioname']
                    ptp_params['radioname'] = club_callsign + ptp_params['radioname']
                else:
                    ptp_params['netaddress'] = self._getInterfaceNetwork(iface['addr_id'])
        return ptp_params

    def getRouterParameters(self,info, device_id, club_callsign):

        router_params = {}
        dhcpblocks = []
        count = 0
        for iface in info:
            if count == 0:
                count = 1
                router_params['sys_name'] = iface['device_name']
                router_params['routername'] = iface['device_name']
            if iface['addr_id'] is not None and (iface['if_type'] == 'ether' or iface['if_type'] == 'wlan'):
                ifname = iface['if_name'] + '_ip'
                router_params[ifname] = self._getInterfaceIp(iface['addr_id'])
                if iface['if_type'] == 'wlan':
                    router_params['radioname'] = club_callsign + iface['device_name']
                    router_params['wlanaddress'] = self._getInterfaceNetwork(iface['addr_id'])
                else:
                    router_params['netaddress'] = self._getInterfaceNetwork(iface['addr_id'])
            elif iface['dhcp_id'] is not None and iface['if_type'] == 'dhcp':
                query = """SELECT pool.pool_name, ipn.ip_address as network, ipl.ip_address as lower_addr, 
                            ipu.ip_address as upper_addr, 
                            (SELECT x.ip_address FROM ip_addresses x WHERE x.id = pool.gateway_addr) as gateway_addr, 
                            (SELECT y.ip_address from ip_addresses y WHERE y.id = pool.dns_addr) as dns_addr
                            FROM dhcp_pools pool
                            INNER JOIN ip_addresses ipn
                            ON ipn.id = pool.network
                            INNER JOIN ip_addresses ipl
                            ON ipl.id = pool.lower_addr
                            INNER JOIN ip_addresses ipu
                            ON ipu.id = pool.upper_addr
                            WHERE pool.id = ?"""
                dhcp = self.getSingleRowQueryDictionary(query, iface['dhcp_id'])
                dhcpblocks.append(dhcp)
        if len(dhcpblocks) > 0:
            router_params['dhcp'] = dhcpblocks
        return router_params

    def getDeviceParameters(self, device_id, club_callsign):
        info = self._getEquipmentInfo(device_id)
        if info[0]['group_id'] == 1 or info[0]['group_id'] == 2:
            return self.getRouterParameters(info, device_id, club_callsign)
        elif info[0]['group_id'] == 3:
            return self.getPTPParams(info, device_id, club_callsign)





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
