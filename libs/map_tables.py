# Map Tables


class MapTables(object):
    """
    Mapping tables are used to map template names to database values.
    This class provides the mapping dictionaries used by applications
    As new entities are added to or remove from templates or the database, the
    mapping tables will need tobe update.

    After the user initializes the MapTables object, they can access the table
    using hte 'Get...' methods.
    """
    def __init__(self):
        self.dhcp_dict = {
            'DP_DHCP_POOL': 'pool_name',
            'DP_DHCP_NETWORK': 'network',
            'DP_DHCP_LOWER_ADDR': 'lower_addr',
            'DP_DHCP_UPPER_ADDR': 'upper_addr',
            'DP_DHCP_GATEWAY_ADDR': 'gateway_addr',
            'DP_DHCP_DNS_ADDR': 'dns_addr',
        }

        self.map_dict = {'DP_ETHER1_IP': 'ether1_ip',
                    'DP_DHCP': 'dhcp',
                    'DP_NETWORK_ADDRESS': 'network_address',
                    'DP_OSPF_NETWORK_ADDRESS': 'ospf_network_address',
                    'DP_OSPF_ROUTER_ID': 'ospf_router_id',
                    'DP_RADIO_NAME': 'radio_name',
                    'DP_REMOTE_IP': 'remote_ip',
                    'DP_REMOTE_ROUTER_NAME': 'remote_router_name',
                    'DP_ROUTER_NAME': 'router_name',
                    'DP_ROUTER_SSID': 'ptp_router_ssid',
                    'DP_ROUTER_SSID_KEY': 'ptp_router_key',
                    'DP_SYS_NAME': 'sys_name',
                    'DP_VRRP1_IP': 'vrrp1_ip',
                    'DP_WLAN1_IP': 'wlan1_ip',
                    'GP_CALL_SIGN': 'call_sign',
                    'GP_CLUB_CONTACT': 'club_contact',
                    'GP_DNS1_IP': 'dns1_ip',
                    'GP_DNS2_IP': 'dns2_ip',
                    'GP_LOGGING1_IP': 'logging1_ip',
                    'GP_LOGGING2_IP': 'logging2_ip',
                    'GP_NTP1_IP': 'ntp1_ip',
                    'GP_NTP2_IP': 'ntp2_ip',
                    'GP_TIMEZONE': 'timezone',
                    'SP_OSPF_KEY': 'ospf_key',
                    'SP_CLIENT_PASSWORD': 'client_password',
                    'SP_CLIENT_SSID': 'client_ssid',
                    'SP_VRRP_KEY': 'vrrp_key',
                    'TP_ETHER1': 'ether1_interface',
                    'TP_ETHER2': 'ether2_interface',
                    'TP_ETHER3': 'ether3_interface',
                    'TP_ETHER4': 'ether4_interface',
                    'TP_ETHER5': 'ether5_interface',
                    'TP_ETHER6': 'ether6_interface',
                    'TP_ETHER7': 'ether7_interface',
                    'TP_ETHER8': 'ether8_interface',
                    'TP_WLAN1': 'wlan1_interface',
                    'TP_WLAN2': 'wlan2_interface',
                    'TP_VRRP1': 'vrrp1_interface'
                    }


    def GetDHCPDict(self):
        """
        Returns the mapping dictionary for DHCP parameters
        """
        return self.dhcp_dict

    def GetMapDict(self):
        """
        Returns the mapping dictionary for all remaining parameters
        """
        return self.map_dict

