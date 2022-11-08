# Building a Sector Router template
The steps for building a template are straight forward:
 1) dump an existing device for class
 2) Identify what items will change from device to device
 3) Map the changes to configuration tags

Let's start by looking at a configuration file for a Sector Router. 
## Goal of a Sector Router
    1. Provide PTMP connections to Clients
    2. DHCP Service for Clients
    3. Default Gateway for routing trafic
    4. Route trafic between clients and the site Bridge/Router

# Step 1 - dumping an exiting device
## Sector Router Configuration File model = RB912UAG-5HPnD-US
Below is a dump of a configuration file for a Switch/Router
### Dump File

#Interfacs -------------------------------------------------------------------  
/interface wireless  
set [ find default-name=wlan1 ] band=5ghz-onlyn channel-width=10mhz country="united states" disabled=no frequency=5920 frequency-mode=superchannel mode=ap-bridge ssid=<span style="color:red">*WAConnect*</span> wireless-protocol=nv2

/interface wireless channels  
add band=5ghz-onlyn comment="Cell sites radiate this at 0 degrees (north)" frequency=5920 list=HamWAN name=Sector1-5 width=5
add band=5ghz-onlyn comment="Cell sites radiate this at 0 degrees (north)" frequency=5920 list=HamWAN name=Sector1-10 width=10
	
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik	

/interface vrrp  
add authentication=ah interface=ether1 name=<span style="color:blue">*vrrp1*</span> password=<span style="color:red">*ABBABBABB*</span> version=2

#Routing ---------------------------------------------  
/routing ospf instance  
set [ find default=yes ] distribute-default=if-installed-as-type-1 in-filter=AMPR-default out-filter=AMPR-default redistribute-connected=as-type-1 redistribute-other-ospf=as-type-1 redistribute-static=as-type-1 router-id=<span style="color:red">*44.12.128.129*</span>

/routing filter  
add action=accept chain=AMPR-default prefix=44.0.0.0/8 prefix-length=8-32  
add action=accept chain=AMPR-default prefix=0.0.0.0/0  
add action=reject chain=AMPR-default  

/routing ospf interface  
add authentication=md5 authentication-key=<span style="color:red">*ABBABBABB*</span> interface=<span style="color:blue">*ether1*</span> network-type=broadcast

/routing ospf network  
add area=backbone network=<span style="color:red">*44.12.128.112/28</span>
	
#General IP

/ip pool  
add name=<span style="color:red">*pool1*</span> ranges=<span style="color:red">*44.12.128.130-44.12.128.141*</span>

/ip dhcp-server  
add address-pool=<span style="color:red">*pool1*</span> disabled=no interface=<span style="color:blue">*wlan1*</span> lease-time=1h name=<span style="color:blue">*dhcp1*</span>

/ip neighbor discovery-settings  
set discover-interface-list=!dynamic  

/ip settings  
set send-redirects=no  

/ip address  
add address=<span style="color:red">*44.12.128.114/28</span> interface=<span style="color:blue">*ether1*</span> network=<span style="color:red">*44.12.128.112*</span>  
add address=<span style="color:red">*44.12.128.129/28*</span> interface=<span style="color:blue">*wlan1*</span> network=<span style="color:red">*44.12.128.128*</span>   
add address=<span style="color:red">*44.12.128.142*</span> disabled=yes interface=<span style="color:blue">*vrrp1*</span> network=<span style="color:red">*44.12.128.128*</span>  

/ip firewall mangle  
add action=change-mss chain=output new-mss=1378 protocol=tcp tcp-flags=syn tcp-mss=!0-1378  
add action=change-mss chain=forward new-mss=1378 protocol=tcp tcp-flags=syn tcp-mss=!0-1378  

/ip service  
set ssh port=222

#SNMP ------------------------------------------------------------------  
/snmp  
set contact=<span style="color:red">*"Spokane DEM"*</span> enabled=yes

#System ----------------------------------------------------------------  
/system logging action  
set 3 remote=<span style="color:red">*44.12.140.4*</span>  

/system clock  
set time-zone-autodetect=no time-zone-name=<span style="color:red">*America/Los_Angeles*</span>  
/system identity  
set name=<span style="color:red">*S1.fancher*</span>  
/system logging  
add action=remote topics=!debug,!snmp  
/system ntp client  
set enabled=yes primary-ntp=<span style="color:red">*44.12.140.4*</span> secondary-ntp=<span style="color:red">*44.12.140.5*</span>  

### End of Dump

# Step 2 - Identify what items will change from device to device
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
servers.

The interface ids will only change if you have multiple interface of hte same
type active in a device.

# Step 3 - Map the changes to configuration tags
The following mapping table is used to map template parameters to database parameters:

| Template_name           | param_dict         | dict_name            |
|-------------------------|--------------------|----------------------|
| SP_CLIENT_PASSWORD      | security_parameters | client_password      |
| SP_CLIENT_SSID          | securty_parameters | client_ssid          |
| GP_CLUB_CONTACT         | global_parameters  | club_contact         |
| GP_DNS1_IP              | global_parameters  | dns1                 |
| GP_DNS2_IP              | global_parameters  | dns2                 |
| TP_ETHER1               | text_parameters    | ether1               |
| DP_ETHER1_IP            | device_parameters  | ether1_ip            |
| GP_LOGGING1_IP          | global_parameters  | logging1_ip          |
| GP_LOGGING2_IP          | global_parameters  | logging2_ip          |
| DP_NETWORK_ADDRESS      | device_parameters  | network_address      |
| GP_NTP1_IP              | global_parameters  | ntp1_ip              |
| GP_NTP2_IP              | global_parameters  | ntp2_ip              |
| SP_OSPF_KEY             | security_parameters | ospf_key             |
| DP_OSPF_NETWORK_ADDRESS | device_parameters  | ospf_network_address |
| DP_OSPF_ROUTER_ID       | device_parameters  | ospf_router_id       |
| DP_RADIO_NAME           | device_parameters  | radio_name           |
| DP_REMOTE_IP            | device_parameters  | remote_ip            |
| DP_REMOTE_ROUTER_NAME   | device_parameters  | remote_router_name   |
| DP_ROUTER_NAME          | device_parameters  | router_name          |
| DP_SYS_NAME             | device_parameters  | sys_name             |
| GP_TIMEZONE             | global_parameters  | timezone             |
| SP_VRRP_KEY             | security_parameters | vrrp_key             |
| TP_VRRP1                | text_parameters    | vrrp1                |
| DP_VRRP1_IP             | device_parameters  | vrrp1_ip             |
| DP_WLAN1_IP             | device_parameters  | wlan1_ip             |
| TP_WLAN1                | text_parameters    | wlan1                |
