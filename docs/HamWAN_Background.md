# Introduction to HamWAN

HamWAN is a modern, multi-megabit, IP-based, digital network for amateur radio use!

HamWAN is a non-profit organization developing best practices for high speed amateur 
radio data networks. HamWAN also runs the Puget Sound Data Ring in Washington State as 
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



## Allocating addresses
How you allocate IP addresses will depend on the number of addresses you receive. Traditionally, 
one (1) class 'C' network is allocated for PTP Backbone, and one (1) class 'C' for device 
ethernet interface IPs. The remaining address are then allocated out, equal size blocks of
powers of 2, to the sector routers and cell routers in (min of four (4) blocks per cell). 
Typically, blocks of sixteen (16) with a network mask of/28 are used. The allocation are 
made until all blocks are allocated. Using our example of 1024 addresses, with one (1) 
class 'C' for PTP and one (1) class 'C' (total 512 addresses) we would have 512 addresses 
left, giving us 32 blocks of 16 addresses. 

You want to allocate more blocks to those sites which have more clients.

### Minimum number of PTP addresses
PTP networks use /31 networks which is one pair of adjacent IP addresses (one for each end
of the PTP link). We currently allocate 256 addresses for P2P, allowing for 128 connections.
If the number of P2P connections are less than 64, then you only need 128 address, and the 
site routers and P2P wlan can share a 256 network address space.

# Selecting Equipment
HamWAN has recommendations for each of the components in the system. There 
are multiple devices select, which will all allow for various designs of
client, and backbone connections.

For our systems we are using the following devices:

Backbone Device: Mikrotik Net Metal 5 - RB922UAGS-5HPacD-NM
Sectors: Mikrotik RB912UAGPnD + StationBox S
