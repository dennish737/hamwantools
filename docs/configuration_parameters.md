# Configuration Parameters and Templates
As stated in the beginning our goal was to be able to configure the network components for our networks. 
To do this we will use our database to extract the parameters needed for a device. These parameters are
then inserted into our templates to construct a configuration file. In this document we will
discuss what parameters are needed for each device, then discuss each of the templates for 
the different devices. The final section will discuss the tools for generating the device
configuration files.

As we built out the network we discussed a hierarchy organization of Organizations, Sites, and Paths.
Where Sites would have Device, and Interfaces, and Paths were used to connect sites and clients (primarily
backbone PTP connections).

The same is true for 'parameters'. There are parameters that are applied across all the equipment the
organization owns (e.g. Call Sign, dns services, logging services, etc.), parameters that are specific for a Site,
parameters for a Site, etc. Our choices of where different parameters are applied, depend on
our goals of:
 1. Ease of configuration
 2. Reliability
 3. Network Security and Stability
 4. Performance
 5. ...

For example, we could supply one 'key' for all the services, have separate key for each site,
or use a single VRRP id, for all devices. The problems of doing these things is having a single
'key' is a security risk, having separated keys makes configuration harder and having a single
VRRP id reduces performance. 

So like our hierarchical for site, devices and interfaces, we want to have a simular model
for parameters that can be applied at different levels in our structure, with the lowest level 
parameters taking precedence over higher levels.

We need to be a little careful here, what we can do and what we should do are quite different. 
For example, though we could apply SSID and password at the 'Device Level',  like we might do for
backbone PTP connections, it would be best if we used the same SSID and password for all the 
sectors on a site if not all the sectors in the network, simplifying the client configuration.

In the DB design, and build we took into account theses various constraints, and provided examples
of how to enter the data in the DB for various scenarios.

We are now ready to begin the development of our tools for building configuration files for our 
devices, and will be using the concept of Templates and Parameters. First we develop a template 
to configure a class of Devices (e.g. router, sector, ptp, client, ...). Determine what items in the template
are fixed for the type of device, and what items will change from Device to Device. We then develop 
a set of query tools for extracting the needed data from the database, and link these parameters
to a 'tag' in the template. Finally, we substitute the template tags wih the actual DB parameters.

For our design, each device class ( bridge/router, sector router, ptp router)will have its 
own template. We will also have different templates for different physical devices of the same class
(e.g. a new or different switch).

## Templates
Templates are used to configure a class of Devices and sets of 'command', 'action', 'attributes'.
For any given command, there may be many actions, and each action will have its own set of attributes.
attributes are sent as 'key'='value' separated by a space(e.g. address=192.16.88.1  interface=local ...).
Some 'attributes', are fixed for a given device(e.g. frequency=5700 disabled=no), while others we 
will need to be changed based on site characteristics (e.g. IP addresses, SSID, key values etc.).
To do that we add a parameter 'key' to the attribute value (e.g. address=if_ether_ip). and as we
generate the config file, substitute the parameter value.

To simplify the configuration, template files are broken into sections

 * Interfaces  
Devices (equipment) have multiple physical interfaces, and each interface has a set of parameters.
Requesting the interface parameters, returns a set of parameters for all the device interfaces.
 * Routing  
The routing sections contains all the routing parameters for the device
 * Global_IP  
The global_ip section provides the ip parameters used for all devices at a site
 * SNMP  
The snmp section provides the snmp configuration information.
 * System  
general system and security site settings

Each of these sections has a separate 'parser' which reads that section of the template file and substitutes the
parameters

## Parameters
Parameters are the things that change from Device to Device (e.g. identity, ip addresses, etc.). As we have discussed, we allow 
parameters to be defined at multiple levels and rules of precedence:

 * Global - default parameters to use for a device, if no site or device parameter is specified
 * Site   - parameters that are specific to a Site
 * Device - Parameters that are specific to a device
 * Path   - Parameters that apply to a specific path

These parameters are read and merged into a single set of parameters based on the rule sof residence.

Parameters are identified as a key value pair, where the key is a tag used in the Template, 
and the value is the value to be substituted.



### Global Parameters
Global parameters provide information which is common site throughout the network. Global parameters
are used if there is no equivalent site parameter. 
The system parameters are as follows:
 * call_sign : the club call sign
 * contact : the person or group to contact when there is problems
 * snmp_community : network system community
 * timezone: the network timezone
 * log1: primary logging server
 * log2: secondary logging server
 * dns1: primary dns server
 * dns2: secondary dns server
 * ntp1: primary ntp server
 * ntp2: secondary server
 * vrrp_id: virtual router protocol identifier
 * wireless: ssid wireless network SSID
 * backbone: ssid of backbone

In addition to the global parameters there is a set of global security keys
 * wirelesskey: 
 * backbonekey:
 * vrrpkey:
 * ospfkey:

The following SQL query will return the system parameters for each device at site 1 for our example:
```sql
SELECT o.call_sign, o.club_contact, gp.timezone, 
    gp.log1, gp.log2, gp.dns1, gp.dns2, gp.ntp1, gp.ntp2,			
FROM organizations o
INNER JOIN global_params gp
    ON gp.org_id = o.org_id AND gp.site_id = 0
WHERE o.org_id = (SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'YOUR CLUB');
```
And for security parameters
```sql
SELECT tag, password 
FROM services_pwd
WHERE site_id is NULL AND org_id = (SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'example_club');
```

### Site Parameters

 * contact : the person or group to contact when there is problems
 * snmp_community : network system community
 * log1: primary logging server
 * log2: secondary logging server
 * dns1: primary dns server
 * dns2: secondary dns server
 * ntp1: primary ntp server
 * ntp2: secondary server

In addition to the site parameters there is a set of site security keys
 * client_ssid: 
 * client_password
 * ptp_ssid:
 * ptp_password
 * vrrpkey:
 * ospfkey:

### Device Parameters
#### Bridge/Router and Sector Router Parameters
 1. sys_name
 2. routername
 3. ether1_ip
 4. ospf_ip
 5. netaddress
 6. ospf_netaddr
 7. wlan1_ip
 8. wlanaddress
 9. radioname
 10. vrrp1
 11. vrrp1network
 12. dhcp
     * pool_name
     * network
     * lower_addr
     * upper_addr
     * gateway_addr
     * dns_addr

If a device does not have a wireless or vrrp interface, 
no parameters are returned. Likewise for DHCP

### Path Parameters
 1. sys_name
 2. routername
 3. ether1_ip
 4. ospf_ip
 5. netaddress
 6. ospf_netaddr
 7. wlan1_ip
 8. remoteip
 9. _from
 10. _to
 11. radioname
 12. remote_router_name

# Parameter Tags
The various global, site, device, path and security parameters are mapped to 'tags'
that are used in our templates for configuring devices. As we have mentioned, we have rules
for selecting the correct parameters that are available in general and site settings.
The tools we use are a set of query that extract the and merge the parameters into s set of 
dictionaries. These dictionaries are then used by the parser to substitute the parameter
value for the template 'tag' name.
## Parameter Dictionary
There are four (4) dictionaries that are used to hold the parameters. These are:
 - Security Parameters (SP)
 - Global Parameters (GP)
 - Text Parameters (TP)
 - Device Parameters (DP) : this includes path parameters for PTP connections

To make sure we use the correct dictionary for parameter substitution we add a two (2)
character prefix to parameter name, identifying the dictionary (e.g. SP, GP, ...)
## Parameter Tags
The following mapping table is used to map template parameters to database parameters:

| Template_name           | param_dict          | parameter_name       |
|-------------------------|---------------------|----------------------|
| SP_CLIENT_PASSWORD      | security_parameters | client_password      |
| SP_CLIENT_SSID          | securty_parameters  | client_ssid          |
| GP_CLUB_CONTACT         | global_parameters   | club_contact         |
| GP_DNS1_IP              | global_parameters   | dns1                 |
| GP_DNS2_IP              | global_parameters   | dns2                 |
| TP_ETHER1               | text_parameters     | ether1               |
| DP_ETHER1_IP            | device_parameters   | ether1_ip            |
| GP_LOGGING1_IP          | global_parameters   | logging1_ip          |
| GP_LOGGING2_IP          | global_parameters   | logging2_ip          |
| DP_NETWORK_ADDRESS      | device_parameters   | network_address      |
| GP_NTP1_IP              | global_parameters   | ntp1_ip              |
| GP_NTP2_IP              | global_parameters   | ntp2_ip              |
| SP_OSPF_KEY             | security_parameters | ospf_key             |
| DP_OSPF_NETWORK_ADDRESS | device_parameters   | ospf_network_address |
| DP_OSPF_ROUTER_ID       | device_parameters   | ospf_router_id       |
| DP_RADIO_NAME           | device_parameters   | radio_name           |
| DP_REMOTE_IP            | device_parameters   | remote_ip            |
| DP_REMOTE_ROUTER_NAME   | device_parameters   | remote_router_name   |
| DP_ROUTER_NAME          | device_parameters   | router_name          |
| DP_SYS_NAME             | device_parameters   | sys_name             |
| GP_TIMEZONE             | global_parameters   | timezone             |
| SP_VRRP_KEY             | security_parameters | vrrp_key             |
| TP_VRRP1                | text_parameters     | vrrp1                |
| DP_VRRP1_IP             | device_parameters   | vrrp1_ip             |
| DP_WLAN1_IP             | device_parameters   | wlan1_ip             |
| TP_WLAN1                | text_parameters     | wlan1                |
