# Configuration Parameters and Templates
As stated in the beginning our goal was to be able to configure the network components for our networks. 
To do this we will use our database to extract the parameters needed for a device. These parameters are
then inserted into our templates to construct a configuration file. In this document we will
discuss what parameters are needed for each device, then discuss each of the templates for 
the different devices. The final section will discuss the tools for generating the device
configuration files.

As we built out the network we discussed a hierarchy organization of Organizations, Sites, and Paths.
Where Sites would have Device, and Interfaces, and Paths were used to connect devices (primarily
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
sectors on a site if not all the sectors in the network.

To implement our device and interface configuration, by using the concept of Templates and Parameters. First we develop a template to configure
a class of Devices (e.g. router, sector, ptp, client, ...), Determine what changes from Device to Device,
and identify those items as parameters in the template.

Each device class will have it own Template

## Templates
Templates are used to configure a class of Devices and sets of 'command', 'action', 'attributes'.
For any given command, there may be many actions, and each action will have its own set of attributes.
attributes are sent as 'key'='value' separated by a space(e.g. address=192.16.88.1  interface=local ...).
Some 'attributes', are fixed for a given device(e.g. frequency=5700 disabled=no), while others we will need to be changed.
To do that we add a parameter 'key' to the attribute value (e.g. address=if_ether_ip). and as we
generate the config file, substitute the parameter value 

To simplify the configuration, template files are broken into sections

 * Interfaces  
Devices (equipment) have multiple physical interfaces, and each interface has a set of parameters.
Requesting the interface parameters, returns a set of parameters for all the device interfaces.
 * Routing  
The routing sections contains all the routing parameters for the device
 * Global_IP  
The global_ip section provides the ip parameters used for all devices
 * SNMP  
The snmp section provides the snmp configuration information.
 * System  
general system and site settings

Each of these sections has a separate 'parser' which reads that section of the template file and substitutes the
parameters

## Parameters
Parameters are the things that change from Device to Device (e.g. identity, ip addresses, etc.). As we have discussed, we allow 
parameters to be defined at multiple levels and rules of precedence:

 * Global - parameters that apply to the network a large
 * Site   - parameters that are specific to a Site
 * Device - Parameters that are specific to a device
 * Path   - Parameters that apply to a specific path

When a parser is invoked, the parameters for each group are provided, and the parser determines which parameter ot use
based on precedence rules.

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
 * vrrp_id: virtual router protocol identifier
 * wireless: ssid wireless network SSID
 * backbone: ssid of backbone

In addition to the site parameters there is a set of site security keys
 * wirelesskey: 
 * backbonekey:
 * vrrpkey:
 * ospfkey:

### Device Parameters


### Path Parameters