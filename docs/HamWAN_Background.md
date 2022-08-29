# Introduction to HamWAN

HamWAN is a modern, multi-megabit, IP-based, digital network for amateur radio use!

HamWAN is also a non-profit organization developing best practices for high speed amateur 
radio data networks and runs the Puget Sound Data Ring in Washington State as 
a real-world network implementation of their proposed designs.

The HamWAN Data Ring has cells deployed at numerous wide-coverage sites. These sites 
are interconnected with radio modems and routed with Open Shortest Path First (known 
by the acronym OSPF). This forms a redundant high-speed backbone to route traffic 
between sites and to the internet.

![HamWAN1](./images/HamWAN_Network.jpg "Simplified diagram of a HamWAN network")

Each Cell Site consist of equipment to connect Clients with the backbone and 
thus the internet, through a Gateway Site. Connections to a Client, can be done through
a radio modem. The radio frequencies used by the backbone network are different that those 
used for client connections, to prevent interference. Also, Client connections use frequencies 
allocated to amateur radio (HAMs). While Backbone connections do not.

![HamWAN2](./images/CellSite_Block.jpg "HamWAN Cell Site Block Diagram")

![HamWAN2](./images/GatewaySite_Block.jpg "HamWAN Gateway Site Block Diagram")

Essentially HamWAN is a WISP (Wireless Internet Service Provider) with a class A network address
space, that will share that address space with licensed Ham Radio Clubs.

## HamWan Components

### Bridge/Router
#### Goals of a Bridge/Router
    1. Route trafic to different elements on the site
    2. Ruute trafic to different sites through PTP Connections
    3. Provide fixed or DHCP Addresses to site equipment
    4. If a gateway site, provide access to the internet via ISP

#### Overview
Each site has a 'Bridge/Router' that manages the site, providing the fixed and dhcp IP 
addresses for the ether interfaces of the site devices (sector and PTP). This device is configured as a 
bridge, mapping all wired interfaces to a single ip address. The device also has ospf routes to
for sector and ptp connection. 

This device is assigned a sixteen address block from the site IP allocation.

Troubleshooting tip: Mikrotik allow adding comment tags to interface, routes, etc. When adding a port
to a bridge, we can add comments to identify what the connection is going to

### Sector Router
#### Goals of a Sector Router
    1. Provide PTMP connections to Clients
    2. DHCP Service for Clients
    3. Default Gateway for routing trafic
    4. Route trafic between clients and the site Bridge/Router

#### Overview
The sector router connects to the site Bridge/Router through the ether interface, and connect to clients
though a wireless connection to the Clients. Each sector covers a 120 degree area, and three (3) sectors are required 
for 360 degrees. 

When a Client connects to a sector, they receive an IP address from a DHCP server. These IP addresses 
are assigned to the sector router in blocks from the IP address allocation. 
The typical block size of sixteen (16) addresses is used, but block sizes that are larger or 
smaller can be used. The only requirement is the block size be a power of two (2).

The frequencies used for sector client connections are HAM frequencies and must not use encryption.

### Backbone PTP Router
#### Goals of PTP Router
    1. Route Trafic between two sites

#### Overview
The backbone ptp routers are used to interconnect the sites through PTP wireless. These routers are 
connected to the Bridge/Router via ethernet interface  (etherN) and have a fix IP address provide by the 
Bridge/Router, and toe another Site via the wireless interface.
These wireless routers do
not use Ham Frequencies, allowing the use of secure communications between sites. PTP connections use
/31 networks, requiring a pair of IP address that are equidistant apart. We need one pair of addresses
for each path. 

## Allocating addresses to subnets
How you allocate IP addresses will depend on the number of addresses you receive. Traditionally, a 2048 block
(8 class C networks) is assigned to a club. One group of 256 addresses (one (1) class 'C' network) is 
allocated for PTP Backbone, and is broken down into /31 networks of 2 adjacent IP addresses.
Another group of 256 addresses routing interface IPs. The remaining address are then divided into blocks of
sixteen (16) addresses each and are reserved for the site switch and sector equipment, with each 
switch getting one block, and each sector getting 2 blocks, one active and one reserved. The reserved
address blocks can be reassigned later to those site with larger client requirements.

### Minimum number of PTP addresses
PTP networks use /31 networks which is one pair of adjacent IP addresses (one for each end
of the PTP link). We currently allocate 256 addresses for P2P, allowing for 128 connections.
If the number of P2P connections are less than 64, then you only need 128 address, and the 
site routers and P2P wlan can share a 256 network address space.

## OSPF Routing
Each OSPF router passes along information about the routes and costs they’ve heard about to all of their 
adjacent OSPF routers, called neighbors.

OSPF routers rely on cost to compute the shortest path through the network between themselves and a remote 
router or network destination. The shortest path computation is done using Djikstra’s algorithm. This 
algorithm isn’t unique to OSPF. Rather, it’s a mathematical algorithm that happens to have an obvious 
application to networking.

Each subnet is connected to other subnets via an ospf router.

Another important idea in OSPF is that interfaces used to exchange information with OSPF neighbors have different types. There are too many types to discuss here but you should be aware of two important ones.

AnOSPF broadcast interface is connected to a shared network, like Ethernet.

AnOSPF point-to-point interface is connected to a link where there can only be a single OSPF router on 
either end, such as a WAN link or a purpose-built Ethernet link.
The reason for the various interface types is to make sure that all routers know about all routes from all 
other routers.

On point-to-point links, there’s no mystery — the two routers know they’re the only OSPF routers on the 
link, and so they exchange routes with each other.

On broadcast links, there’s a potential for many different OSPF routers to be on the network segment. 
To minimize the number of neighbor relationships that form on broadcast links, OSPF elects a designated 
router (as well as a backup) whose job it is to neighbor with all other OSPF routers on the segment and 
share everyone’s routes with everyone else.

# Selecting Equipment
HamWAN has recommendations for each of the components in the system. There 
are multiple devices select, which will all allow for various designs of
client, and backbone connections.

For our systems we are using the following devices:

Bridge/Router Switch - CRS112-8P-4S
Backbone Device: Mikrotik Net Metal 5 - RB922UAGS-5HPacD-NM
Sectors: Mikrotik RB912UAGPnD + StationBox S
