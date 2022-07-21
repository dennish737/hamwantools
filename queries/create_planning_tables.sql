-- Planning data base tables
-- this file creates the tables for the planning data base
-- once created the user can add information to the tables
-- to construct their network
--
-- Version 1.0.0

--PRAGMA foreign_keys = OFF;

commit;
BEGIN TRANSACTION;
--DROP TABLE IF EXISTS "organizations";
CREATE TABLE IF NOT EXISTS "organizations" (
    -- identifies the organization. In most cases there is only one organization in the data base
    -- but this feature allows you to segment your network and have areas of ownership, while still providing
    -- centralize management.
	"org_id"	INTEGER NOT NULL,
	"state"	TEXT,
	"county"	TEXT,
	"state_region_id"	INTEGER,
	"friendly_name"	TEXT,
	"club_name"	TEXT NOT NULL UNIQUE,
	"club_contact"	TEXT,
	"ptp_net_size"	INTEGER NOT NULL DEFAULT 256,   -- number of ip addresses reserve for PTP connections (2 per PTP path + )
	"device_net_size"	INTEGER NOT NULL DEFAULT 256,   -- number of ip addresses reserved for equipment (min 1 per ether if + 1 vrrp)
	"block_size"	INTEGER NOT NULL DEFAULT 16,    -- min number of ip addresses added to a dhcp pool
	"share_ptp_net" INTEGER NOT NULL DEFAULT 0,     -- split a single class C network between PTP and Devices
	PRIMARY KEY("org_id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "config_templates";
CREATE TABLE IF NOT EXISTS "config_templates" (
    "id" INTEGER NOT NULL,
    "org_id" INTEGER,
    "name" TEXT,
    "file" TEXT,
    "version" TEXT,
    FOREIGN KEY("org_id") REFERENCES "organizations"("org_id"),
    PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "equipment_groups";
CREATE TABLE IF NOT EXISTS "equipment_groups" (
    -- the equipment groups allow us to define the different pieces of equipment that are used in the
    -- network. It also allows us to link the configuration templates, used to configure the devices
	"id"	INTEGER NOT NULL,
	"group_name" TEXT NOT NULL UNIQUE, --group name (router, sector, bptp, cptmp, gateway and default_gaeway
	"description"	TEXT NOT NULL,
	"suffix"	TEXT NOT NULL,  -- name suffix. device names are site.group_suffixn where
	                            -- suffix are R, S, PTP, CTMP, GW, DGW, and n is the number [1...n], DGW defines the virtual router(s)
	"config_id" INTEGER,
	"interface_list" json,          -- devices can have multiple interfaces
	FOREIGN KEY(config_id) REFERENCES "config_templates"(id),
	PRIMARY KEY("id" AUTOINCREMENT)
);


--DROP TABLE IF EXISTS "site_types";
CREATE TABLE IF NOT EXISTS "site_types" (
    -- site_types:
        -- cell: a standard cell site with PTP and SECTOR connections to other cells and clients -> cell
        -- gateway: A cell site with a connection to an internet provider -> gw
        -- client: A client site -> c
	"id"	INTEGER NOT NULL,
	"description"	TEXT NOT NULL,
	"identifier"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "path_types";
CREATE TABLE IF NOT EXISTS "path_types" (
    "id"	INTEGER NOT NULL,
    "description" TEXT NOT NULL,
    "identifier" INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

-- service passwords.
-- Services are items like wireless network, vrrp, etc that
-- require individual routers to join the group
-- this table provide the a service of service passwords
--DROP TABLE IF EXISTS "services_pwd";
CREATE TABLE IF NOT EXISTS "services_pwd" (
	"id"	INTEGER NOT NULL,
	"org_id" INTEGER NOT NULL,
	"tag"	TEXT NOT NULL,  -- wirelesskey, backbonekey, vrrpkey, ospfkey or ospgkeyn for multiple areas
	"passwd"	TEXT NOT NULL,
	FOREIGN KEY(org_id) REFERENCES organizations("org_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "organizations";
CREATE TABLE IF NOT EXISTS "organizations" (
    -- identifies the organization. In most cases there is only one organization in the data base
    -- but this feature allows you to segment your network and have areas of ownership, while still providing
    -- centralize management.
	"org_id"	INTEGER NOT NULL,
	"state"	TEXT,
	"county"	TEXT,
	"state_region_id"	INTEGER,
	"friendly_name"	TEXT,
	"club_name"	TEXT NOT NULL UNIQUE,
	"club_contact"	TEXT,
	"ptp_net_size"	INTEGER NOT NULL DEFAULT 256,   -- number of ip addresses reserve for PTP connections (2 per PTP path + )
	"device_net_size"	INTEGER NOT NULL DEFAULT 256,   -- number of ip addresses reserved for equipment (min 1 per ether if + 1 vrrp)
	"block_size"	INTEGER NOT NULL DEFAULT 16,    -- min number of ip addresses added to a dhcp pool
	"share_ptp_net" INTEGER NOT NULL DEFAULT 0,     -- split a single class C network between PTP and Devices
	PRIMARY KEY("org_id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "general_params";
CREATE TABLE IF NOT EXISTS "general_params" (
    -- There are several parameters that HamWAN uses that are organization wide
    -- These include:
        -- the SSID name used for client connections (wireless_name)
        -- The SSID used to identify the backbone network (backbone_name)
        -- The network time zone (time_zone)
    -- The choice of having separate or the same SSID for client and backbone is up to
    -- the organization.
    "id" INTEGER NOT NULL,
    "org_id" INTEGER NOT NULL,
    "wireless_name" TEXT NOT NULL,
    "backbone_name" TEXT NOT NULL,
    "time_zone" TEXT,
    UNIQUE ("org_id")
    FOREIGN KEY ("org_id") REFERENCES organizations("org_id")
    PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "network_services";
CREATE TABLE IF NOT EXISTS "network_services" (
    -- network_services, the services like DNS, NTP and Logging are systems are required for the network
    -- once these networks are set up, the other network devices will use then.
    -- Currently the only known service types are dns, ntp and logging
    "id" INTEGER NOT NULL,
    "org_id" INTEGER NOT NULL,
    "service_type" TEXT NO NULL,
    "service_name" TEXT NOT NULL,
    "service_ip" INTEGER,
    FOREIGN KEY ("org_id") REFERENCES organizations("org_id"),
    FOREIGN KEY (service_ip) REFERENCES ip_addresses(id),
    PRIMARY KEY("id" AUTOINCREMENT)

);

--DROP TABLE IF EXISTS "network_allocations";
CREATE TABLE IF NOT EXISTS "network_allocations" (
    -- Address allocation are provided by HamWan, and then sub divided down for the network
    -- in theory, you can get multiple allocations, and different allocation for each organization
    -- blocks_created is set to 1 when the addresses are allocated out to the network
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"network_allocation"	TEXT NOT NULL,
	"starting_address"	TEXT NOT NULL,
	"ending_address"	TEXT NOT NULL,
	"subnet_mask"	INTEGER NOT NULL,
	"blocks_created"	INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY("org_id") REFERENCES organizations("org_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "ip_types";
CREATE TABLE IF NOT EXISTS "ip_types" (
    -- There are three ip types in the network:
    --  pool: ip addresses that are allocated to DHCP pools as needed
    --  ptp: ip addresses  that are to be allocated to ptp addresses
    --  devices ip addresses to be allocated to the devices ether addresses
    "id"	INTEGER NOT NULL,
    type_name TEXT NOT NULL UNIQUE,
    PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "ip_addresses";
CREATE TABLE IF NOT EXISTS "ip_addresses" (
    -- Given an allocation, an entry is generated for each ip address
    -- the reserved field allows ot to assign ip_addresses to pools and ptp blocks
    -- the non zero value of reserved represent the address_block or ptp_block that reserved
    -- the address
    -- the value of the assigned field, represent the interface the address is assigned to
    -- 0  means unassigned
    -- new is set to zero after the ip addresses is added, assigned a type and if pool or ptp
    -- reserved.
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"ip_address"	TEXT NOT NULL UNIQUE,
	"ip_type"	INTEGER NOT NULL,
	"reserved"	INTEGER DEFAULT 0 NOT NULL,
	"assigned" INTEGER DEFAULT 0 NOT NULL,
	"new" INTEGER DEFAULT 1 NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY ("org_id") REFERENCES organizations (org_id),
	FOREIGN KEY ("ip_type") REFERENCES ip_types (id)
);

--DROP TABLE IF EXISTS "address_blocks";
CREATE TABLE IF NOT EXISTS "address_blocks" (
    -- pool address blocks
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"network"	INTEGER NOT NULL,
	"start_ip"	INTEGER NOT NULL,
	"end_ip" INTEGER NOT NULL,
	"broadcast" INTEGER NOT NULL,
	"num_ip" INTEGER NOT NULL,
	"new"   INTEGER DEFAULT 1 NOT NULL,
	"assigned"	TEXT DEFAULT NULL,
	"linked" INTEGER DEFAULT 0 NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY ("org_id") REFERENCES organizations (org_id),
	FOREIGN KEY ("network") REFERENCES ip_addresses (id),
	FOREIGN KEY ("start_ip") REFERENCES ip_addresses (id),
	FOREIGN KEY ("end_ip") REFERENCES ip_addresses (id),
	FOREIGN KEY ("broadcast") REFERENCES ip_addresses (id)
);

--DROP TABLE IF EXISTS "sites";
CREATE TABLE IF NOT EXISTS "sites" (
    -- the cell or client site information
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"site_type" INTEGER NOT NULL,
	"name"	TEXT NOT NULL UNIQUE,
	"Owner"	TEXT,
	"contact"	TEXT,
	"lat"	REAL,
	"lon"	REAL,
	"num_routers" INTEGER DEFAULT 0 NOT NULL,
	"num_sectors" INTEGER DEFAULT 0 NOT NULL,
	"num_ptp" INTEGER DEFAULT 0 NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY ("org_id") REFERENCES organizations (org_id),
	FOREIGN KEY ("site_type") REFERENCES site_types(id)
);

--DROP TABLE IF EXISTS "site_equipment";
CREATE TABLE IF NOT EXISTS "site_equipment" (
    -- equipment assigned to a site
	"id"	INTEGER NOT NULL,
	"site_id"	INTEGER NOT NULL,
	"group_id"   INTEGER NOT NULL,
	"name"	TEXT DEFAULT NULL,
	"serial_num"	TEXT DEFAULT NULL,
	"model"	TEXT DEFAULT NULL,
	"active" INTEGER DEFAULT 0 NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY ("site_id") REFERENCES sites(id),
	FOREIGN KEY ("group_id") REFERENCES equipment_groups(id)
);

DROP TABLE IF EXISTS "paths";
CREATE TABLE IF NOT EXISTS "paths" (
    -- wireless path between sites. Most commonly used for PTP paths, but can also
    -- be used to document multiple paths to a client
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"type_id"   INTEGER NOT NULL,
	"site_a"	INTEGER NOT NULL,
	"site_b"	INTEGER NOT NULL,
	"ptp_block"  INTEGER,
	"device_a"   INTEGER,
	"device_b"   INTEGER,
	"name"	    TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY ("org_id") REFERENCES organizations(org_id),
	FOREIGN KEY ("type_id") REFERENCES path_types(id),
	FOREIGN KEY ("site_a") REFERENCES sites(id),
	FOREIGN KEY ("site_b") REFERENCES sites(id),
	FOREIGN KEY ("ptp_block") REFERENCES ptp_block(id),
	FOREIGN KEY ("device_a") REFERENCES site_equipment(id),
	FOREIGN KEY ("device_b") REFERENCES site_equipment(id),
	UNIQUE(site_a, device_a),
	UNIQUE(site_b,device_b),
	UNIQUE(ptp_block)
);

--DROP TABLE IF EXISTS "ptp_blocks";
CREATE TABLE IF NOT EXISTS "ptp_blocks" (
    -- ptp address block
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"ip_a"	INTEGER NOT NULL,
	"ip_b"	INTEGER NOT NULL,
	"new"   INTEGER DEFAULT 1,
	"assigned"	INTEGER DEFAULT NULL,
	FOREIGN KEY("ip_a") REFERENCES "ip_addresses"("id"),
	FOREIGN KEY("ip_b") REFERENCES "ip_addresses"("id"),
	FOREIGN KEY("assigned") REFERENCEs "paths"("id"),
	FOREIGN KEY("org_id") REFERENCES "organizations"("org_id"),
	UNIQUE("ip_a"),
	UNIQUE("ip_b")
	PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "interfaces";
CREATE TABLE IF NOT EXISTS "interfaces" (
    --physical network interfaces
    "id" INTEGER NOT NULL,
    "equip_id" INTEGER NOT NULL,
    "if_type" TEXT  NOT NULL,
    "if_name" TEXT NOT NULL,
    "addr_id" INTEGER,
    "new" INTEGER DEFAULT 1 NOT NULL,
    FOREIGN KEY ("addr_id") REFERENCES ip_addresses("id"),
    UNIQUE("equip_id", "if_name")
    PRIMARY KEY("id" AUTOINCREMENT)
    );

COMMIT;

--PRAGMA foreign_keys = ON;