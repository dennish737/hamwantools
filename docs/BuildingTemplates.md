# Building templates
The steps for building a template are straight forward:
 1) dump an existing device for class
 2) Identify what items will change from device to device
 3) Map the changes to configuration tags

We have three classes of equipment we need to consider:
 1) Site/Switch Router 
 2) Sector Router
 3) PTP Router
 4) 
Let's start by looking at a configuration file for a Site/Switch Router (for
now we will assume this is not a gateway switch).
## Goals of the Site/Switch Router
    1. Route trafic to different elements on the site
    2. Route trafic to different sites through PTP Connections
    3. Provide fixed or DHCP Addresses to site equipment

# Step 1 - dump an existing device for class
## Switch Router Configuration File CRS112-8P-4S
Below is a dump of a configuration file for a Switch/Router
### Dump File

#Interfaces ----------------------------------------

/interface bridge
add name=bridge1

/interface bridge settings  
set use-ip-firewall=yes use-ip-firewall-for-pppoe=yes use-ip-firewall-for-vlan=yes

/interface bridge port  
add bridge=bridge1 comment=defconf interface=ether1  
add bridge=bridge1 comment=defconf interface=ether2  
add bridge=bridge1 comment=defconf interface=ether3  
add bridge=bridge1 comment=defconf interface=ether4  
add bridge=bridge1 comment=defconf interface=ether5  
add bridge=bridge1 comment=defconf interface=ether6  
add bridge=bridge1 comment=defconf interface=ether7  
add bridge=bridge1 comment=defconf interface=ether8  
#note ssp ports do not need to be assigned if not used  
add bridge=bridge1 comment=defconf interface=sfp9  
add bridge=bridge1 comment=defconf interface=sfp10  
add bridge=bridge1 comment=defconf interface=sfp11  
add bridge=bridge1 comment=defconf interface=sfp12  


/interface ovpn-server server  
set cipher=aes256 enabled=yes

/interface wireless security-profiles  
set [ find default=yes ] supplicant-identity=MikroTik


#Routing -------------------------------------------------------  
/routing ospf instance  
set [ find default=yes ] distribute-default=if-installed-as-type-1 in-filter=AMPR-default out-filter=AMPR-default 
redistribute-bgp=as-type-1 redistribute-connected=as-type-1 redistribute-other-ospf=as-type-1 router-id=<span style="color:red">*44.12.128.113*</span>

/routing filter  
add action=accept chain=AMPR-default prefix=44.0.0.0/8 prefix-length=8-32  
add action=accept chain=AMPR-default prefix=0.0.0.0/0  
add action=reject chain=AMPR-default  

/routing ospf interface  
add authentication=md5 authentication-key=<span style="color:red">*ABBABBABB*</span> interface=<span style="color:blue">ether6</span> network-type=broadcast

/routing ospf network  
add area=backbone network=<span style="color:red">*44.12.128.112/28*</span>

#global ip -------------------------------------------------

/ip address  
add address=<span style="color:red">*44.12.128.113/28*</span> interface=<span style="color:blue">*ether1*</span> network=<span style="color:red">*44.12.128.112*</span>  
 

/ip hotspot profile
set [ find default=yes ] html-directory=flash/hotspot

/ip dns
set allow-remote-requests=yes servers=<span style="color:red">*8.8.8.8,8.8.4.4*</span>

#SNMP -----------------------------------------------

#System ---------------------------------------------  
/system identity  
set name=<span style="color:red">*R1.fancher*</span>

#SNMP ------------------------------------------------------------------  
/snmp  
set contact=<span style="color:red">*"Spokane DEM"*</span> enabled=yes

#System ----------------------------------------------------------------
/system logging action  
set 3 remote=<span style="color:red">*44.12.140.4*</span>

/system clock
set time-zone-autodetect=no time-zone-name=<span style="color:red">*America/Los_Angeles*</span>  

/system identity  
set name=<span style="color:red">*R1.fancher*</span>

/system logging  
add action=remote topics=!debug,!snmp  
/system ntp client  
set enabled=yes primary-ntp=<span style="color:red">*44.12.140.4*</span> secondary-ntp=<span style="color:red">*44.12.140.5*</span>  

### End of File

# Step 2 -Identify what items will change from device to device
Note that we have rearranged our file into our sections:
 1) Interfaces
 2) Routing
 3) Global_IP
 4) SNMP
 5) System

Note that we have also identified all the items thant need to change in
<span style="color:red">*red*</span> and interface names in <span style="color:blue">*blue*</span>

Note items in <span style="color:blue">*blue*</span> are interfaces id. Devices can have multiple
interfaces of the same type (e.g. ether, wlan, vrrp, etc.) as well as multiple dhcp servers. We number
interfaces of each type starting at 1 (e.g. ether1, ether2, ..., wlan1, wlan2, etc.). The same for DHCP
servers. To allow for multiple interface, we use text_parameters to map the interface name

# Step 3 - Map the changes to configuration tags
## Mapping
The following mapping table is used to map template parameters to database parameters:

| Template_name           | param_dict         | DB Name              |
|-------------------------|--------------------|----------------------|
| DP_DHCP_DNS_ADDR        | device_parameters  | dns_addr             |
| DP_DHCP_GATEWAY_ADDR    | device_parameters  | gateway_addr         |
| DP_DHCP_LOWER_ADDR      | device_parameters  | lower_addr           |
| DP_DHCP_NETWORK         | device_parameters  | network              |
| DP_DHCP_POOL            | device_parameters  | pool_name            |
| DP_DHCP_UPPER_ADDR      | device_parameters  | upper_addr           |
| DP_ETHER1_IP            | device_parameters  | ether1_ip            |
| DP_NETWORK_ADDRESS      | device_parameters  | network_address      |
| DP_OSPF_NETWORK_ADDRESS | device_parameters  | ospf_network_address |
| DP_OSPF_ROUTER_ID       | device_parameters  | ospf_router_id       |
| DP_RADIO_NAME           | device_parameters  | radio_name           |
| DP_REMOTE_IP            | device_parameters  | remote_ip            |
| DP_REMOTE_ROUTER_NAME   | device_parameters  | remote_router_name   |
| DP_ROUTER_NAME          | device_parameters  | router_name          |
| DP_ROUTER_SSID          | device_parameters  | ptp_router_ssid      |
| DP_ROUTER_SSID_KEY      | device_parameters  | ptp_router_key       |
| DP_SYS_NAME             | device_parameters  | sys_name             |
| DP_VRRP1_IP             | device_parameters  | vrrp1_ip             |
| DP_WLAN1_IP             | device_parameters  | wlan1_ip             |
| GP_CLUB_CONTACT         | global_parameters  | club_contact         |
| GP_DNS1_IP              | global_parameters  | dns1                 |
| GP_DNS2_IP              | global_parameters  | dns2                 |
| GP_LOGGING1_IP          | global_parameters  | logging1_ip          |
| GP_LOGGING2_IP          | global_parameters  | logging2_ip          |
| GP_NTP1_IP              | global_parameters  | ntp1_ip              |
| GP_NTP2_IP              | global_parameters  | ntp2_ip              |
| GP_TIMEZONE             | global_parameters  | timezone             |
| SP_OSPF_KEY             | security_parameters | ospf_key             |
| SP_CLIENT_PASSWORD      | security_parameters | client_password      |
| SP_CLIENT_SSID          | securty_parameters | client_ssid          |
| SP_VRRP_KEY             | security_parameters | vrrp_key             |
| TP_ETHER1               | text_parameters    | ether1               |
| TP_ETHER2               | text_parameters    | ether2               |
| TP_ETHER3               | text_parameters    | ether3               |
| TP_ETHER4               | text_parameters    | ether4               |
| TP_ETHER5               | text_parameters    | ether5               |
| TP_ETHER6               | text_parameters    | ether6               |
| TP_ETHER7               | text_parameters    | ether7               |
| TP_ETHER8               | text_parameters    | ether8               |
| TP_WLAN1                | text_parameters    | wlan1                |
| TP_WLAN2                | text_parameters    | wlan2                |
| TP_VRRP1                | text_parameters    | vrrp1                |


### Mapped File
/interface bridge
add name=bridge1

/interface bridge settings  
set use-ip-firewall=yes use-ip-firewall-for-pppoe=yes use-ip-firewall-for-vlan=yes

/interface bridge port  
add bridge=bridge1 comment=defconf interface=ether1  
add bridge=bridge1 comment=defconf interface=ether2  
add bridge=bridge1 comment=defconf interface=ether3  
add bridge=bridge1 comment=defconf interface=ether4  
add bridge=bridge1 comment=defconf interface=ether5  
add bridge=bridge1 comment=defconf interface=ether6  
add bridge=bridge1 comment=defconf interface=ether7  
add bridge=bridge1 comment=defconf interface=ether8  
#note ssp ports do not need to be assigned if not used  
add bridge=bridge1 comment=defconf interface=sfp9  
add bridge=bridge1 comment=defconf interface=sfp10  
add bridge=bridge1 comment=defconf interface=sfp11  
add bridge=bridge1 comment=defconf interface=sfp12  


/interface ovpn-server server  
set cipher=aes256 enabled=yes

/interface wireless security-profiles  
set [ find default=yes ] supplicant-identity=MikroTik


#Routing -------------------------------------------------------  
/routing ospf instance  
set [ find default=yes ] distribute-default=if-installed-as-type-1 in-filter=AMPR-default out-filter=AMPR-default 
redistribute-bgp=as-type-1 redistribute-connected=as-type-1 redistribute-other-ospf=as-type-1 router-id=<span style="color:red">*DP_OSPF_ROUTER_ID*</span>

/routing filter  
add action=accept chain=AMPR-default prefix=44.0.0.0/8 prefix-length=8-32  
add action=accept chain=AMPR-default prefix=0.0.0.0/0  
add action=reject chain=AMPR-default  

/routing ospf interface  
add authentication=md5 authentication-key=<span style="color:red">*SP_OSPF_KEY*</span> interface=<span style="color:blue">TP_ETHER6</span> network-type=broadcast

/routing ospf network  
add area=backbone network=<span style="color:red">*DP_OSPF_NETWORK_ADDRESS/28*</span>

#global ip -------------------------------------------------

/ip address  
add address=<span style="color:red">*DP_ETHER1_IP/28*</span> interface=<span style="color:blue">*TP_ETHER1*</span> network=<span style="color:red">*DP_NETWORK_ADDRESS*</span>  
 

/ip hotspot profile
set [ find default=yes ] html-directory=flash/hotspot

/ip dns
set allow-remote-requests=yes servers=<span style="color:red">*GP_DNS1_IP,GP_DNS2_IP*</span>

#SNMP -----------------------------------------------

#System ---------------------------------------------  
/system identity  
set name=<span style="color:red">*DP_ROUTER_NAME*</span>

#SNMP ------------------------------------------------------------------  
/snmp  
set contact=<span style="color:red">*"GP_CLUB_CONTACT"*</span> enabled=yes

#System ----------------------------------------------------------------
/system logging action  
set 3 remote=<span style="color:red">*GP_LOGGING1_IP*</span>

/system clock
set time-zone-autodetect=no time-zone-name=<span style="color:red">*GP_TIMEZONE*</span>  

/system identity  
set name=<span style="color:red">*DP_ROUTER_NAME*</span>

/system logging  
add action=remote topics=!debug,!snmp  
/system ntp client  
set enabled=yes primary-ntp=<span style="color:red">*GP_NTP1_IP*</span> secondary-ntp=<span style="color:red">*GP_NTP2_IP*</span>  


### Interfaces
For the Bridge/Router (Site Switch) we create a *bridge* and add all the 
ethernet ports to the bridge interface. This allows all the ethernet ports
to share a common address. In our case, the switch has 8 RJ54 (ethernet) 
ports, and 4 sfp (Small Form Factor) ports. The SFP port support fiber, cat5, cat6, cat6a and cat7
interfaces.  
If the device is acting as a GateWay, we will need to reserve one port
for the connection to the ISP, and the remaining ports are then assigned to
the bridge.

<span style="color:orange">*TBD port 6*</span>

The next interface is an Open Virtual Private Network server. Here we enable the service
and the set the cipher

### Routing
In this section we set up the ospf routing information. For this section
we need the following parameters:
    1. ospf router id
    2. ospf network for this device
    3. The OSPF-Key


### Mapped Template
This is the final text template with the color coding removed, for the switch router can be found in
[../templates/r_router_template.txt](../templates/r_router_template.txt).

Template for sector router can be found in [../templates/s_router_template.txt](../templates/s_router_template.txt).

Template for the ptp router can be found in [../templates/ptp_router_template.txt](../templates/ptp_router_template.txt).

# Step 4 - Building a configuration file
At this point e have a template where we could query the DB for the 
configuration information, using parameter table tool, and manually substitute 
the column values returned to our template and create a configuration file that 
could be uploaded and run to configure the device. But, we would rather automate this process.

Let's stat by taking a closer look at our 'configuration file'. 
 - The first thing we notice is that the basic structure is 'command -> action -> parameters'
where a command may have multiple actions, and an action can have multiple parameters.
 - Parameters are 'name value pairs', in the format name=value 
(e.g. interface=TP_ETHER6 , router-id=DP_OSPF_ROUTER_ID, etc.). 
If a parameter has multiple parameters (a list of values), the values are separated 
by a comma (,) (e.g. servers=GP_DNS1,GP_DNS2) 
 - Commands: commands are split into groups and organized in hierarchical levels 
(this is comparable to disk directories) with the 'root' level indicated by '/'
with each level separated by a space (e.g. /ip, /ip address, /system clock)
 - Following the command is an action word (add, edit, find, move, print, remove, 
set, ...)
 - Following the action word are the parameters
 - Comments are identified with a'#' in column 1
 - Last but not least, the action word and parameters must be on a single line

<p style="text-align: center;">Warning</p>  

```text
RouterOS allows you to move relative to your current 'location' in the command 
tree and does not require a leading '/'. As a convention, we will always use a 
'/', in column 1, to make sure we start from the root of the command tree.
```

We can also note, that for any command, not all parameters require a DB lookup. 
This is because these parameters are 'constant' throughout the HamWan system for the
equipment selected. Also, not all configuration parameters for a command are specified.
Essentially, we ignore these parameters and 'pass them through'.

## Template Parsers 
To automate the building of a config file, we will use the Template Parser tools.
There are two template parsers available:
 - basic_parser which can parse our simple text file we have generated
 - advance_parser which can parse a json file representation of our config file.

Thus far we have focussed on a 'basic' approach where we are using the model described by
hamwan.org by replicating the 'model'. Because of that we can use an existing configuration
to build up our templates.

If you are starting from scratch, selecting your own equipment, the simple approach
may not be sufficient, and provide all the configuration ability you need. 
The advance_parser allows additional configuration capability, such as site specific 
options, non-standard equipment, mixed equipment, etc. But requires an indepth 
knowledge of how to build out an ISP service.

The design of the basic_parser can be found in [BasicParser](./BasicParser.md).

The design and construction of templates for the advance_parser are found in [AdvanceParser](./AdvanceParser.md).

