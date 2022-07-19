-- Planning data base tables
-- this file creates the tables for the planning data base
-- once created the user can add information to the tables
-- to construct their network
--
-- Version 1.0.0

--PRAGMA foreign_keys = OFF;
--DROP TABLE IF EXISTS "equipment_groups";
CREATE TABLE IF NOT EXISTS "equipment_groups" (
	"id"	INTEGER NOT NULL,
	"group_name" TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	"suffix"	TEXT NOT NULL,
	"interfaces" json,
	PRIMARY KEY("id" AUTOINCREMENT)
);


--DROP TABLE IF EXISTS "site_types";
CREATE TABLE IF NOT EXISTS "site_types" (
	"id"	INTEGER NOT NULL,
	"description"	TEXT NOT NULL,
	"identifier"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "path_types";
CREATE TABLE IF NOT EXISTS "path_types" (
    "id"	INTEGER NOT NULL,
    "description" TEXT NOT NULL,
    "identifier" INTEGER NOT NULL,
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
	"tag"	TEXT NOT NULL,
	"passwd"	TEXT NOT NULL,
	FOREIGN KEY(org_id) REFERENCES organizations("org_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "organizations";
CREATE TABLE IF NOT EXISTS "organizations" (
	"org_id"	INTEGER NOT NULL,
	"state"	TEXT,
	"county"	TEXT,
	"state_region_id"	INTEGER,
	"friendly_name"	TEXT,
	"club_name"	TEXT NOT NULL UNIQUE,
	"club_contact"	TEXT,
	"ptp_net_size"	INTEGER NOT NULL DEFAULT 256,
	"device_net_size"	INTEGER NOT NULL DEFAULT 256,
	"block_size"	INTEGER NOT NULL DEFAULT 16,
	"share_ptp_net" INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("org_id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "general_params";
CREATE TABLE IF NOT EXISTS "general_params" (
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
    "id" INTEGER NOT NULL,
    "org_id" INTEGER NOT NULL,
    "service_type" TEXT NO NULL,
    "service_name" TEXT NOT NULL,
    "service_ip" TEXT,
    FOREIGN KEY ("org_id") REFERENCES organizations("org_id")
    PRIMARY KEY("id" AUTOINCREMENT)

);
--DROP TABLE IF EXISTS "network_allocations";
CREATE TABLE IF NOT EXISTS "network_allocations" (
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
    "id"	INTEGER NOT NULL,
    type_name TEXT NOT NULL UNIQUE,
    PRIMARY KEY("id" AUTOINCREMENT)
);

--DROP TABLE IF EXISTS "ip_addresses";
CREATE TABLE IF NOT EXISTS "ip_addresses" (
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

--DROP TABLE IF EXISTS "paths";
CREATE TABLE IF NOT EXISTS "paths" (
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
	FOREIGN KEY ("org_id") REFERENCES organizations(id),
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