# Database and Other Tools
## Introduction
As stated in the planning document it is important to document your network. Again there are 
a several way to do this, and you should use a method that you are conformable with. Because of the complexity
of networks, and the multiple pieces of information that needs to be tracked, I have chosen
to use a SQLite Database. The key reasons for using a DB are:
    - After initial load it is easy to maintain
    - Able to add and link data items to configuration parameters
    - Able to develop queries and tools for getting configuration parameters reducing manual error
    - Able to develop queries and tools for adding, deleting and moving data items
    - Able to build tools to generate configuration file for devices
    - Able to easily add new devices and configuration parameters to the network
    - Able to build tools to 'map' the network
    - SQLite is supported on Windows, linux and Mac platforms.
    - Database is a file, which can be shared and made profitable

For tool development I have chosen to use Python3. Python3 is supported by Windows, linux and Mac,
is object-oriented, and well documented and supported.

Another major technology use is JSON. YAML was considered, but SQLite support or YAML is not available
at the time of writing.

### Installing SQLite
To install SQLite on your platform, use your favorite search engine and search for 'install sqlite on "platform"'.
Here is a list of sites I used to install/verify SQLite  
 - [macOS](https://flaviocopes.com/sqlite-how-to-install/)
 - [Windows](https://www.sqlitetutorial.net/download-install-sqlite/)
 - [Ubuntu Linux](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-sqlite-on-ubuntu-20-04)

You can also find sqlite downloads at [SQLite]{https://www.sqlite.org/download.html)

In addition to SQLite, you may want to donwload 
[sqlite tool](https://www.sqlitetutorial.net/download-install-sqlite/#:~:text=The%20SQLiteStudio%20tool%20is%20a,CSV%2C%20XML%2C%20and%20JSON.)
and [DB Browser](https://sqlitebrowser.org/dl/)

We use DB Browser for sql queries.

### Installing Python
To install SQLite on your platform, use your favorite search engine and search for 
'install python on <platform>'.
Here are a list of sites I used for installing Python:  
 - [macOS](https://docs.python-guide.org/starting/install3/osx/)
 - [Windows](https://www.howtogeek.com/197947/how-to-install-python-on-windows/)
 - [Ubuntu Linux](https://www.how2shout.com/linux/how-to-install-python-3-and-pip-3-on-ubuntu-20-04-lts/)

### Other requirements
For additional requirements please see the [ReadMe](../README.md)


## Database Design
In our discussion [Planning Your Network](./PlanningYourNetwork.md) we talked about sites, equipment 
and path (primarily backbone PTP paths). We also talked about getting a block of addresses for
your network, and creating an organization to build and control the site. Each of these translates
into a database table, with additional tables for address blocks and ptp blocks and ip_addresses.

As we build out the DB, python tools were written to build out tables. For example on site equipment,
the input is a CSV file, but we do not require the equipment name. Instead, the tools automatically
build the name for you. 


### DB Schema
The following is an image of the DB schema:
![DB Schema](./images/DBSchema.JPG)

TBD - add description of tables

## Creating the DB, adding tables and  types

### Creating 
 1) open DB Browser
 2) Select New Database
 3) Charge to the directory where you want the DB stored (../hamwantools/data)
 4) Enter the file name and use the .sqlite3 suffix
 5) Click Save

#### Adding Tables
 1) open DB Browser
 2) Open your database 
 3) Select the Execute SQL tab (red) and select the open file (blue)
![create tables](./images/dbbrowser_createtbls.jpg)
 4) Select the ../query/create_planning_tables.sql
 5) Click the run button ![Run Create Table](./images/dbbrowser_createexec.jpg)

#### Adding cdir table
CIDR stands for Classlesss Inter-Domain Routing. It enables network administrators to group 
blocks of IP addresses into single routing networks. 

CIDR accomplishes the same task as traditional subnet masking

This table is provided as a support tool for looking up CIDR value

 1) open DB Browser
 2) Open your database 
 3) select File -> Import
 4) select the file ./examples/cidr_mask.csv
 5) click Ok

#### Add type information for Sites, Equipment, Interfaces, ...
 1) open DB Browser
 2) Open your database 
 3) Select the Execute SQL tab and select the open file
 4) Select the ../query/add_types.sql
 5) Click the run button

### Add Organization
All sites, paths and equipment are associated with an Organization, and the organization is responsible
for the installation, maintenance and disposal of the equipment assigned to the organization.

 1) open the ./queries/add_org.sql in DB Browser Execute SQL window
 2) Edit the file for your organization
 3) Click the run button

### Adding your Sites
To add sites, we are going to use the tool add_sites.py (./tools/add_sites.py). In our 
[Planning Your Network](./PlanningYourNetwork.md) discussion, we created a list of sites in a csv file.
Our tool can use a .csv file to enter multiple sites (see [equipment_example](../examples/site_example.csv))

Before running the tool, use the ../examples/site_example.csv as a template to create your
information. Once done editing the template, run the tool to add your sites.  

Example: python ./tools/add_sites.py -c example_club --csv ./examples/site_example.csv --db ./data/planning_example.sqlite3

### Adding your Backbone PTP paths
Next we want to add our backbone path information (BPTP). In our 
[Planning Your Network](./PlanningYourNetwork.md) discussion, we created a list of paths in a csv file.

Before running the tool, use the ../examples/path_example.csv as a template to create your
information. Once done editing the template, run the tool to add your paths. 

Example:  python ./tools/add_paths.py -c example_club --csv ./examples/path_example.csv --db ./data/planning_example.sqlite3

### add Security information
There are several 'keys' that are required to allow the various routers and switches
to inter connect. You can set the keys for a 'site', for the network as a whole or
both. The database has a service_keys table that allow you to assign keys at the 
network and site levels. 
By leaving the 'site' number blank, defines a default set of keys that are applied network
wide. If a site id is provided, then the site keys will override the default keys.

 1) open the ./queries/add_service_keys.sql in DB Browser Execute SQL window
 2) Edit the key_val values for your organization
 3) Click the run button

### Add Global Parameters
General parameters can be applied to the network or site level of the network. These parameters
include but are not limited to:
 - logging
 - dns
 - ntp
 - time zone

If parameters re entered with a site_id, they are site specific parameters. While if the site_id
is left empty (NULL) they are network parameters. If there are no global site parameters, the network
parameters will be used.

TBD instructions for loading example network global parameters


### Add Equipment to sites

Example: python ./tools/add_equipment.py -c example_club --csv ./examples/equipment_example.csv --db ./data/planning_example.sqlite3

### Add Equipment to Paths

Example:python ./tools/add_equipment2path.py -c example_club --db ./data/planning_example.sqlite3

### Add your Interfaces

Example:python ./tools/add_interfaces.py -c example_club --db ./data/planning_example.sqlite3

### Add network allocation
 use add_netaloc.sql
### Construction your allocation and ptp blocks

Example:python ./tools/add_ipaddresses.py -c example_club --db ./data/planning_example.sqlite3

### Add Equipment to the Paths

Example:python ./tools/add_equipment2path.py -c spokane --db ./data/spokane_example.sqlite3

### Add Interfaces

Example:python ./tools/assign_ip2interfaces.py -c spokane --db ./data/spokane_example.sqlite3

### Assign IP Address to Interfaces

Example: python ./tools/assign_ip2interfaces.py -c spokane --db ./data/spokane_example.sqlite3 





