# Building a Bridge/Router template
The steps for building a template are straight forward:
 1) dump an existing device for class
 2) Identify what items will change from device to device
 3) Map the changes to configuration tags

Let's start by looking at a configuration file for a Switch/Router (for
now we will assume this is not a gateway switch).
## Goals of the Switch/Router
    1. Route trafic to different elements on the site
    2. Ruute trafic to different sites through PTP Connections
    3. Provide fixed or DHCP Addresses to site equipment

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
set time-zone-autodetect=no time-zone-name=America/Los_Angeles  

/system identity  
set name=<span style="color:red">*R1.fancher*</span>

/system logging  
add action=remote topics=!debug,!snmp  
/system ntp client  
set enabled=yes primary-ntp=<span style="color:red">*44.12.140.4*</span> secondary-ntp=<span style="color:red">*44.12.140.5*</span>  

### End of File

Note that we have rearranged our file into our sections:
 1) Interfaces
 2) Routing
 3) Global_IP
 4) SNMP
 5) System

Note that we have also identified all the items thant need to change in
<span style="color:red">*red*</span>.

Note items in <span style="color:blue">*blue*</span> are interfaces id. Devices can have multiple
interfaces of the same type (e.g. ether, wlan, vrrp, etc.) as well as multiple dhcp servers. We number
interfaces of each type starting at 1 (e.g. ether1, ether2, ..., wlan1, wlan2, etc.). The same for DHCP
servers. To allow for multiple interface, we use text_parameters to map the interface name

## Mapping
The following mapping table is used to map template parameters to database parameters:

|ETHER1_IP           |device_parameters  |ether1_ip           |
|--------------------|-------------------|--------------------|
|NETWORK_ADDRESS     |device_parameters  |network_address     |
|OSPF_NETWORK_ADDRESS|device_parameters  |ospf_network_address|
|OSPF_ROUTER_ID      |device_parameters  |ospf_router_id      |
|RADIO_NAME          |device_parameters  |radio_name          |
|REMOTE_IP           |device_parameters  |remote_ip           |
|REMOTE_ROUTER_NAME  |device_parameters  |remote_router_name  |
|ROUTER_NAME         |device_parameters  |router_name         |
|SYS_NAME            |device_parameters  |sys_name            |
|VRRP1_IP            |device_parameters  |vrrp1_ip            |
|WLAN1_IP            |device_parameters  |wlan1_ip            |
|CLUB_CONTACT        |global_parameters  |club_contact        |
|DNS1_IP             |global_parameters  |dns1                |
|DNS2_IP             |global_parameters  |dns2                |
|LOGGING1_IP         |global_parameters  |logging1_ip         |
|LOGGING2_IP         |global_parameters  |logging2_ip         |
|NTP1_IP             |global_parameters  |ntp1_ip             |
|NTP2_IP             |global_parameters  |ntp2_ip             |
|TOMEZONE            |global_parameters  |timezone            |
|CLIENT_SSID         |gsecurty_parameters|client_ssid         |
|Template_name       |param_dict         |dict_name           |
|CLIENT_PASSWORD     |security_parameters|client_password     |
|OSPF_KEY            |security_parameters|ospf_key            |
|VRRP_KEY            |security_parameters|vrrp_key            |
|ETHER1              |text_parameters    |ether1              |
|VRRP1               |text_parameters    |vrrp1               |
|WLAN1               |text_parameters    |wlan1               |


### Interfaces
For the Bridge/Router (Site Switch) we create a *bridge* and add all the 
ethernet ports to the bridge interface. This allows all the ethernet ports
to share a common address. In our case, the switch has 8 RJ54 (ethernet) 
ports, and 4 sfp (Small Form Factor) ports. The SFP port support fiber, cat5, cat6, cat6a and cat7
interfaces.  
If the device is acting as a GateWay, we will need to reserve one port
for the connection to the ISP, and the remaining ports are then assigned to
the bridge.

The next interface is an Open Virtual Private Network server. Here we enable the service
and the set the cipher

### Routing
In this section we set up the ospf routing information. For this section
we need the following parameters:
    1. ospf router id
    2. ospf network for this device
    3. The OSPF-Key


### Final Template
#Interfaces ----------------------------------------

/interface bridge add name=bridge1

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
set [ find default=yes ] distribute-default=if-installed-as-type-1 in-filter=AMPR-default out-filter=AMPR-default redistribute-bgp=as-type-1 redistribute-connected=as-type-1 redistribute-other-ospf=as-type-1 router-id=<span style="color:red">*OSPF_ROUTER_ID*</span

/routing filter
add action=accept chain=AMPR-default prefix=44.0.0.0/8 prefix-length=8-32
add action=accept chain=AMPR-default prefix=0.0.0.0/0
add action=reject chain=AMPR-default

/routing ospf interface
add authentication=md5 authentication-key=OSPF_KEY interface=ether6 network-type=broadcast

/routing ospf network
add area=backbone network=<span style="color:red">*OSPF_NETWORK_ADDRESS*</span>

#global ip -------------------------------------------------

/ip address
add address=ETHER1_IP interface=<span style="color:blue">*ETHER1*</span> network=<span style="color:red">*NETWORK_ADDRESS*</span>

/ip hotspot profile set [ find default=yes ] html-directory=flash/hotspot

/ip dns set allow-remote-requests=yes servers=<span style="color:red">*DNS1,DNS2*</span>


#SNMP ------------------------------------------------------------------  
/snmp  
set contact=<span style="color:red">*CLUB_CONTACT*</span> enabled=yes

#System ----------------------------------------------------------------  
/system logging action  
set 3 remote=<span style="color:red">*LOGGING1_IP*</span>

/system clock
set time-zone-autodetect=no time-zone-name=America/Los_Angeles  
/system identity  
set name=<span style="color:red">*SYS_NAME*</span>

/system logging  
add action=remote topics=!debug,!snmp  
/system ntp client  
set enabled=yes primary-ntp=<span style="color:red">NTP1_IP</span> secondary-ntp=<span style="color:red">*NTP2_IP*</span>  

End of File