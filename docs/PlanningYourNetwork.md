# Planning and Building a HamWAN network
## Things to think about 
Before we start planning building 'HamWAN'  network, we should probably get you house in order
and understand the rule. 

Basically we are building a Wireless Internet Service Provider (WISP). To do this we will need to 
make a lot of decisions on Site locations, frequencies, equipment to use, our gateway ISP
providers, etc. This is tru no matter what type of network we would want to build. The advantage 
of using HamWAN as a model, is that HamWAN has already figured out many of the pieces for us, for
an internet like network. Also, HamWAN can supply you with an internet route-able address space . 
But even with all HamWAN design, equipment choices and recommendations, there are many decision 
we will have to make, to design a usable and resilient network.

So in addition to Ham operators with solid RF experience, you will need a source for 
funding, and people who know something about managed networks, access to towers and buildings
for sites, time and patients, legal counsel, etc. So you might want to first  find the people 
around you who are willing to work with you on this project and form a group (a club), to work through the many
decisions and problems we will encounter.
### HamWAN address Space and Equipment Choices
HamWAN controls the allocation of IP addresses, so you will need to file a request
to HamWAN for IP addresses. Before you can do that, though, you will need to have a
legitimate and registered HAM club, with a call sign. we will want this to b a legal entity
to limit the liability of the group members. 

Also, HamWAN uses managed networks devices. If cost were no object, we could build
the network using components form Cisco, UniFi and others. Right now the Puget Sound 
Data Ring is build on Mikrotik, which provides, at reasonable cost, managed network device. 
But these devices are not anything like the routers you buy at Home Depot, Costco, 
Stables or other computer or office supply stores. Also, they do not have the training, and support
like Cisco, Unifi and Big 5. Thus, you may require additional training to support and understand these devices.
Having someone with Network IT, leading the network configuration effort snd being prepared to spend time 
online viewing videos and reading documents, will be needed.

Also, if there is a local Junior College, Technical School or University, nearby, you may want to
look into their IT programs, and available classes.
### Financing your network
In most ham based projects, capital funding is handled by the team putting it together, and operational
cost is ignored. However, for this project you will need to think of both capital funding (money to buy all the equipment
and install it) but also ongoing operating cost (tower rental, equipment failure, etc.). 
Unless your group is extremely wealthy, and can afford to buy and maintain your own sites, equipment,
ISP services, you will probably need to work out business relationships with site owners, to allow you 
to mount your HamWAN equipment at their site and pay regular fees to maintain access. You will
also need to draw up contracts, and other legal documents.

Another choice you have is to link up with a served agency, who appreciates the support of the Ham Radio community
and work with them to establish ongoing location access, funding and support. 
### Security
Security is one of those necessary item that most people do not want to spend a lot of time thinking about.
Unless your sites come with preconfigured security, you can use, you will need to what security items
are needed and how you are going to monitor activity.

In a HamWAN network there are also several security keys/passwords that are required. For example
 1) PTMP SSID and password
 2) PTP SSID and password
 3) VRRP password
 4) OSPF password
 5) Admin passwords
 6) etc.

The reason for these passwords is to protect the system, and keep people off the network that
do not belong. Passwords can be grouped by site or path, or be system-wide. The main thing is
you need to remember them and use them in configurations. 

There are advantages and disadvantages for every password scheme. for example, if you choose to make passwords site specific,
then there will be a lot of passwords to remember and manage, but the system is less susceptible
On the other hand, if you use a single password, it will be easy to remember, but now your 
system is more vulnerable.

The following is the minimum recommendations:
 1) The SSID name and Password for PTMP (client), PTP Clients and PTP Backbone should be different
 2) OSPF Keys for Wired (ether n) and Wireless (wlan n) should be different
 3) VRRP key should be site specific

### Naming Conventions
Names ar used to identify sites, equipment and paths. It is best that you have a consistent naming convention
used throughout the network. In addition, some device will have multiple names, such as a physical
device name and a logical device names, as in the case for ptp devices.

By HamWAN uses the following naming conventions:
 1) names are case-insensitive and unique
 2) names use a doted naming convention for naming for both logical and physical names.   
For physical names the naming convention is 'equipment.site', where equipment, is {r_{n} for  
switches, $s_{n}$ for sector and $ptp_{n}$ for ptp devices. 'n' has values of 1-n where n is the  
total number of devices for that class of devices. Examples of names are:   
     r1.dem, s2.dem, ptp1.dem, etc. 
 3) In addition to the Physical Name, PTP device had a logical name showing the path in at to.from  
format (e.g. dem.site1, site1.dem).. Switches and Sector Devices, logical name are the same as te physical name
 4) sector and ptp radio names are call sign/logical name (e.g. WA7CON/s1.deb). Note that call  
signs are capitalized
 5) It is best to not have spaces or special characters, except '/', '_', and '.' in names. 


### Other Issues
Other rules we need to be careful about are rules for ham band usage. If we use Ham frequencies,
we must first be licensed Ham's,cannot use encryption or secure links or other common network tools to protect te user
and keep a record of activities. 

For HamWAN like networks the client connections are done using ham frequencies, while
backbone services use 'public' non-ham frequencies. Doing so allows communication over the backbone,
like admin traffic, system maintenance, etc. to use secure links. 

Like many things, we do not discuss every technical, legal, financial,
etc., issue we may encounter, and the hurdles a group will go through will differ.
As the group builds out the network design and implementation there will be issues identified
that will need to be address.

As you work through the process, document the issues you discover, so you can make sure there
addresses. And keep remembering there is no one solution, the solution that is best for the group is 
based on the group requirements. 

### Documenting what you do.
As you begin to put your network together, you are going to hit a documentation problem. There are several option for
documenting you network. Some people use Microsoft Word, others use Excel, etc. You need to choose a 
documentation method that allows you to track great details, add, delete, move and change devices.

Everyone has their preferred way of documenting the way you do things, but to be successful, as a group, you
will need to standardize and organize your documentation. Just throwing everything into a shared folder won't
be sufficient, and as team members age out, will leave all your hard work useless.

For our example project I have created a database that will track our activity. Python scripts have
been created to add, remove and edit entries. You are free to use what has been, change it and improve 
upon it, or not use it at all. What is most important is you document what you do so someone else
can follow in your footsteps.

## Getting Started
*"An Idea without a plan is nothing more thant a dream." -Steven A Board*
### A brief diversion
Rather than having a technology, that is looking for a problem, let's turn 
it around aan describe our problem and figure out how technology can solve it.

So what is the problem(s) we are looking to solve? Are we building a network where Ham 
operators get free internet? Are we building a low cost network for emergency preparedness? 
Are we providing a service for one or more served agencies? Are we building a network as
a training tool, to have a team of 'experts' that can deploy networks, when all else fails?

Each of these problems requires a different solution, and in many cases, we may need to solve many problems.

For our example lets assume we two objectives:
 1) are setting up a redundant WISP for our served agencies and provide low cost
SCADA transport for critical services:
    1) Fire
    2) Department of Transportation
    3) Sherif
    4) major Hospitals
    5) Stream Flow data
    6) Seismic Data
 2) Training for setting up and deploying a usable network at an incident command site.

Other than SCADA data the network is not a primary provider,  but will be used by the served
agencies, for network services, when primary network services are down, or as communication to
a remote incident command post.

Other than hospital data, there is no 'security requirement', other than the data cannot be tampered with.
Hospital information must be sent over 'secure' networks.

We need a service that provide wireless access to cover a very large geographical area. We are willing
to give up high speed data for cost, and it is important to the served agencies, that the group running the 
network make the network a priority, and that equipment can be added and removed from the network easily.

During major events like Fire or Earth Quake, we need to be able to network multiple temporary sites
and clients.

Also, during major events where there could be a loss of internet services, our network needs to stand
on it own.

And last but not least, we need a training program to make sure we have adequate qualified 
volunteer staff available.


So what do we need to do to build out to design and build this network?

There are several places that we could start, and the direction we take will be based on priorities. In our case
we will assume it is more important that we build a network to support 'fix location' clients first, then add in
support for temporary cells and clients. Along the way we can add in additional network services (dns, ntp, logging, etc.)
that will allow us to sand as complete, independent network without global internet access.

Se we will start by first determining where our 'fixed location' client are, and the various 
options we have to connect to our clients. Since we are choosing a wireless technology, then we need to locate 'towers'
for our sites, where our clients will have a clear line of site to our access points. Once we have located the 'sites', we
will then connect our site, with a backbone network to our gateway site. 

Once we have completed that, we then can then begin to look at 'temporary' sites and clients.

#### Site Planning
There are three types of sites we need to plan for, Gateway, Cell and Client. Client sites are the easiest, 
they are located at the Clients Location, and connect to the Clients infrastructure. Like other ISP providers
the only thing required from us, is a bridge or router that can connect their network to our 
network. 

Gateway and Cell Sites are simular, with Gateways requiring additional equipment to connect 
the site to an ISP. Usually, Gateway sites are at a served agency and act as both a Gateway, 
Cell Site and maybe a Client.

Cell Sites are used, by the clients, to access the network, and do not require direct access to 
the internet or other clients. 

To estimate the number of cell site needed, requires a more involved process. First you need to make a list of 
available cell sites with potential for good coverage. From that list you can trim it 
down too sites that are accessible and affordable. From there you need to make propagation 
maps, with tools like SPLAT!, Radio Mobile and TAP to determine coverage and make sure all your clients are served. Finally: you need to 
select those sites which give you the most coverage for the least cost.

There is no magic formula or tool for selecting sites, and you need to rely on experience, and your understanding of 
microwave propagation.

### Connecting the Cell Sites (The Backbone)
Once we have our cell sites located, the next step is to determine how the cell sites are
connected. It is best if a cell site is connected to at least two (2) other cells. Doing so
will provide a redundant path in case a site goes down (known as a loop). To improve performance of the backbone,
some sites will require more thant two (2) paths. Again we will use propagation maps between sites to determine
the best connections between sites. We will also make some decisions on our backbone component selection. For example,
the Puget Sound Ring chose 5GHz devices, while Tennessee choose 2.5Ghz. 5GHz give you more bandwidth and speed,  while 
2.5GHz is slower but give you more distance. In our example we are going to use 5GHz devices.
It should be noted that if your client has a need for high reliability networking, they will also need to have 
'redundant clients' pointed to multiple sites, and these redundant connections will need to be counted in the total 
number of clients, and will affect the section of cell sites.

The needs for performance and reliability should be part of your site planning goals.

### Access points 
Now that we have the site location and backbone paths, we need to connect to clients.
Since we are using wireless what we would like to have an 'omnidirectional' Point to Multipoint (PTMP) access
point device. Typically, omnidirectional devices have poor performance when compared to directional 
device, and access points are no exception. To resolve this problem, a device known as a 'sector'
is used. Sector antennas with various beam width, measured in degrees, are arranged to give us
360 degree connection capability. The most common sector antennas are 120 degrees and 
requiring three device to get 360 degree coverage. The number of Sector devices you need at a site
will vary on where your clients are located. For example, if all your clients are within a 120 degree
window, then you will only need a single sector.

We will assume tha sites either have 'none' or three (3) sectors. Typically, Sector one (1) points North, Sector two (2) South East, and Sector three (3) South West.

### Gateways Site
Last but not least, we need to identify the sites that will connect us to the outside world.
These sites are call Gateway Sites. They are exactly the same as every other site, with an additional
piece of equipment to connect the site to and ISP. Usually this equipment is supplied by the ISP, 
and we use this device to connect to the site router, which requires slightly different configuration
of the site switch (router).

### Final Check
Once we have all this information, it is time to document and check. Typically, this is done
by drawing a network map, review the map and verify that all the served agencies needs are met.

## Getting Started
Let's assume that we have done the work and identified the number of clients, where they are located, and
the initial site studies, etc. And determined we need one Gateway, and have 200 clients. The Gateway  Site,
will have no PTMP Connections (no sectors).
To get the coverage we need, we will need to use eight (8) Cell Sites to connect up all the Clients using wireless PTMP connections. 
We also determine that four (4) of the Cell Sites are directly connect to Gateway site though PTP connections,
and each of the remaining 4 Sites will use two wireless PTP connection  to connect to one
of the Sites directly connected to the Gateway. 

![basic network diagram](./images/basicnetwork.jpg).
Figure: Basic Network


Please note that we do not show client connections, and this is a simple network, with limited redundancy. This is done to keep things simple,
so we can focus on the steps. Most likely in your network, you will have multiple Gateway sites and redundant paths to handle
the loss of a cell or gateway site, and if you can afford it, you might have redundant equipment on your sites.

#### Sites and Paths
So at this point we have enough information to document our initial Sites and Paths. Base on the Basic Network figure, we have a Gateway
(GW), eight (8) sites (site1 ... site8) and 12 paths (path1 ... pathC). For documentation purposes, we can document our sites
and paths using a CSV file. The template below adds additional content to the CSV files that may be useful.
There is also example csv files - [../examples/site_example.csv](../examples/site_example.csv) 
and [../examples/path_example.csv](../examples/path_example.csb)  
##### Sites
| name  | site_type | owner | contact | lat | lon |
|-------|-----------|-------|---------|-----|-----|
| GW    | gateway   |       |         |     |     |
| site1 | cell      |       |         |     |     |
| site2 | cell      |       |         |     |     |
| site3 | cell      |       |         |     |     |
| site4 | cell      |       |         |     |     |
| site5 | cell      |       |         |     |     |
| site6 | cell      |       |         |     |     |
| site7 | cell      |       |         |     |     |
| site8 | cell      |       |         |     |     |

##### Paths
| name   | site_a | site_b | type_id |
|--------|--------|--------|---------|
| path1  | gw     | site1  | BPTP    |
| path2  | gw     | site2  | BPTP    |
| path3  | gw     | site3  | BPTP    |
| path4  | gw     | site4  | BPTP    |
| path5  | site1  | site5  | BPTP    |
| path6  | site2  | site6  | BPTP    |
| path7  | site3  | site7  | BPTP    |
| path8  | site4  | site8  | BPTP    |
| path9  | site2  | site5  | BPTP    |
| pathA  | site3  | site6  | BPTP    |
| pathB  | site2  | site7  | BPTP    |
| pathC  | site3  | site8  |BPTP     |

BPTP - Backbone Point To Point: There are two type of PTP paths Client PTP (CPTP) and Backbone PTP (BPTP).
These paths use different frequencies (Bands) to prevent interference, even though they may use the same equipment.
### How many addresses do I need?
Every interface connected to the network requires an IP address. Well isn't the number of 
IP addresses needed the number of devices connected to the network? Nop, devices can have
multiple interfaces connected to the network. Take for example your laptop, it has a wireless 
connection, and it may have a wired connection. 

We are assuming that each client connection is one (1) IP address, but we also need to add in 
the backbone devices (PTP connections) and sector devices. Finally, we need to add in the number
of 'site routers' (one per site). We can use the following formula to compute the number of
addresses needed:

$ nipA = nc + np2p\times 4 + ns\times 2 + n_sites $

where:
    nc is the number of clients
    np2p is the number of p2p connections
    ns is the total number of sectors
    n_sites is the number of sites. 

When we request addresses we need to request  blocks that are powers of 2. Unless you live in an extremely remote area,
we should ask for at least 1024 addresses. In our case we will be asking for 2048 addresses.

#### Document what we have
At this time we should have the following information:
 1) And Organization or Club, with a charted
 2) Identified Gateways, Cell Sites and Clients 
 3) A list of names and locations for the Gateway, Cell Site and Clients
 4) A list of backbone ptp paths (BPTP), creating the backbone of the network
 5) A list of client and their locations
 6) An estimate of the number of IP addresses you will need (include extra addresses for spares and growth)
 7) Submitted a request to HamWAN for an address Block
 8) We have a basic diagram of our network.

### Gateway and Site Equipment
Gateway sites and Cell Sites are essentially the same, with Gateway sites having an additional piece of 
equipment to connect to the ISP, and the equipment needed to connect to the ISP is provided by the ISP.
So, lets focus on the equipment need to buy for our Cell sites. There are three (3) types of equipment we need to buy
for a Cell site: 
    1) Site Routers
    2) Sector Routers
    3) PTP Routers
Each site (Gateway or Network) must have a Site Router, and can have zero (0) or more Sector or PTP
routers. Since each Sector router covers 120 degrees, each site can have a maximum of 3 Sector Routers,
and the number of PTP Routers must match the number of PTP paths connecting the site.
For our example network, we assumed that the Gateway Site has no sectors, and four (4) PTP paths, sites 1 and 4
have teo(2) PTP and three Sector, and sites 2 and 3 have four (4)  PTP and three (3) Sector.

A network diagram for a Site is shown below with the interface connections and device names:
![site network diagram](./images/SiteNetworkDIagram.jpg)

#### Equipment List
Next we need to add the equipment to the gateway and each of the sites. For equipment we have chosen
the following Mikrotik products:
 1) Site Router (r<sub>n</sub>)   : CRS112-8P-4S 
 2) Sector Router (s<sub>n</sub>) - 
 3) PTP router (ptp<sub>n</sub>)  : RB922UAGS-5HPacD-NM



| Site  | Equipment Type | Name       |
|-------|----------------|------------|
| gw    | ROUTER         | r1.gw      |
|       | PTP            | ptp1.gw    |
|       | PTP            | ptp2.gw    |
|       | PTP            | ptp3.gw    |
|       | PTP            | ptp4.gw    |
| site1 | ROUTER         | r1.site1   |
|       | PTP            | ptp1.site1 |
|       | PTP            | ptp2.site1 |
|       | SECTOR         | s1.site1   |
|       | SECTOR         | s2.site1   |
|       | SECTOR         | s3.site1   |
| site2 | ROUTER         | r1.site2   |
|       | PTP            | ptp1.site2 |
|       | PTP            | ptp2.site2 |
|       | PTP            | ptp3.site2 |
|       | PTP            | ptp4.site2 |
|       | SECTOR         | s1.site2   |
|       | SECTOR         | s2.site2   |
|       | SECTOR         | s3.site2   |
| site3 | ROUTER         | r1.site3   |
|       | PTP            | ptp1.site3 |
|       | PTP            | ptp2.site3 |
|       | PTP            | ptp3.site3 |
|       | PTP            | ptp4.site3 |
|       | SECTOR         | s1.site3   |
|       | SECTOR         | s2.site3   |
|       | SECTOR         | s3.site3   |
| site4 | ROUTER         | r1.site4   |
|       | PTP            | ptp1.site4 |
|       | PTP            | ptp2.site4 |
|       | SECTOR         | s1.site4   |
|       | SECTOR         | s2.site4   |
|       | SECTOR         | s3.site4   |
| site5 | ROUTER         | r1.site5   |
|       | PTP            | ptp1.site5 |
|       | PTP            | ptp2.site5 |
|       | SECTOR         | s1.site5   |
|       | SECTOR         | s2.site5   |
|       | SECTOR         | s3.site5   |
| site6 | ROUTER         | r1.site6   |
|       | PTP            | ptp1.site6 |
|       | PTP            | ptp2.site6 |
|       | SECTOR         | s1.site6   |
|       | SECTOR         | s2.site6   |
|       | SECTOR         | s3.site6   |
| site7 | ROUTER         | r1.site7   |
|       | PTP            | ptp1.site7 |
|       | PTP            | ptp2.site7 |
|       | SECTOR         | s1.site7   |
|       | SECTOR         | s2.site7   |
|       | SECTOR         | s3.site7   |
| site8 | ROUTER         | r1.site8   |
|       | PTP            | ptp1.site8 |
|       | PTP            | ptp2.site8 |
|       | SECTOR         | s1.site8   |
|       | SECTOR         | s2.site8   |
|       | SECTOR         | s3.site8   |

### Updating Path Information
In our initial Path List, we identified our backbone connection between cell sites. But we did not identify was used to
create the path. Now that we have assigned equipment to the Cells, our next step is to assign PTP equipment to the Paths.

To do this we will start at one site, and assign the equipment to the paths that connect to it, then move to the next cell 
site and repeat the process, until all paths or complete.

#### Path Updates
| name  | site_a | site_b | type_id | device_a   | device_b   |
|-------|--------|--------|---------|------------|------------|
| path1 | gw     | s1te1  | BPTP    | ptp1.gw    | ptp1.site1 |
| path2 | gw     | site2  | BPTP    | ptp2.gw    | ptp1.site2 |
| path3 | gw     | site3  | BPTP    | ptp3.gw    | ptp1.site3 |
| path4 | gw     | site4  | BPTP    | ptp4.gw    | ptp1.site4 |
| path5 | site1  | site5  | BPTP    | ptp2.site1 | ptp1.site5 |
| path6 | site2  | site6  | BPTP    | ptp2.site2 | ptp1.site6 |
| path7 | site3  | site7  | BPTP    | ptp2.site3 | ptp1.site7 |
| path8 | site4  | site8  | BPTP    | ptp2.site4 | ptp1.site8 |
| path9 | site2  | site5  | BPTP    | ptp3.site2 | ptp2.site5 |
| pathA | site3  | site6  | BPTP    | ptp3.site3 | ptp2.site6 |
| pathB | site2  | site7  | BPTP    | ptp4.site2 | ptp2.site7 |
| pathC | site3  | site8  | BPTP    | ptp4.site3 | ptp2.site8 |

### What do we have so far?
At this point we have a basic plan for our network, and the next step is to order equipment, get 
the IP addresses form HamWAN, and get the equipment in to start configuring it.

There are a few more thing we need to think about. Once we get the address we will need to allocate them
to the Devices and sectors.

#### Allocating addresses
How you allocate IP addresses will depend on the number of addresses you receive. Traditionally, 
one (1) class 'C' network is allocated for PTP Backbone, and one (1) class 'C' for device 
ethernet interface IPs. The remaining address are then allocated out, equal size blocks of
powers of 2, to the sector routers and cell routers in blocks. 

Typically, blocks of sixteen (16) addresses with a network mask of/28 are used. The allocation are 
made until all blocks are allocated. Using our example of 1024 addresses, with one (1) 
class 'C' for PTP and one (1) class 'C'  devices (total 512 addresses) we would have 512 addresses 
left, giving us 32 blocks of 16 addresses. 

You want to allocate more blocks to those cell sites which have more clients.

#### Minimum number of PTP addresses
PTP networks use /31 networks which is one pair of adjacent IP addresses (one for each end
of the PTP link). We currently allocate 256 addresses for P2P, allowing for 128 connections.
If the number of P2P connections are less than 64, then you only need 128 address, and the 
site device and P2P can share a class C network address space.





