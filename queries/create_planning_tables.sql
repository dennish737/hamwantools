-- Planning data base tables
-- this file creates the tables for the planning data base
-- once created the user can add information to the tables
-- to construct their network

CREATE TABLE "equipment_types" (
	"id"	INTEGER NOT NULL,
	"description"	TEXT NOT NULL,
	"iddentifier"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "site_types" (
	"id"	INTEGER NOT NULL,
	"description"	TEXT NOT NULL,
	"identifier"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "path_types" (
    "id"	INTEGER NOT NULL,
    "description" TEXT NOT NULL,
    "identifier" INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);


CREATE TABLE "organizations" (
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

CREATE TABLE "network_allocations" (
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"network_allocation"	TEXT NOT NULL,
	"starting_address"	TEXT NOT NULL,
	"ending_address"	TEXT NOT NULL,
	"subnet_mask"	INTEGER NOT NULL,
	"blocks_created"	INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY("org_id") REFERENCES "organizations"("org_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "address_blocks" (
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"start_address"	TEXT NOT NULL UNIQUE,
	"end_address"	TEXT NOT NULL UNIQUE,
	"num_addresses" INTEGER NOT NULL,
	"start_ip_num" INTEGER NOT NULL,
	"end_ip_num" INTEGER NOT NULL,
	"reserved"	TEXT,
	"assigned" INTEGER DEFAULT 0 NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
	FOREIGN KEY ("org_id") REFERENCES organizations (org_id)
);

CREATE TABLE "sites" (
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"site_type" INTEGER NOT NULL,
	"name"	TEXT NOT NULL UNIQUE,
	"Owner"	TEXT,
	"contact"	TEXT,
	"lat"	REAL,
	"lon"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
	FOREIGN KEY ("org_id") REFERENCES organizations (org_id)
	FOREIGN KEY ("site_type") REFERENCES site_types(id)
);

CREATE TABLE "paths" (
	"id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"type_id"   INTEGER NOT NULL,
	"site_a"	INTEGER NOT NULL,
	"site_b"	INTEGER NOT NULL,
	"name"	    TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
	FOREIGN KEY ("org_id") REFERENCES organizations(id)
	FOREIGN KEY ("type_id") REFERENCES path_types(id)
);

CREATE TABLE "equipment" (
	"id"	INTEGER NOT NULL,
	"site_id"	INTEGER NOT NULL,
	"type_id"   INTEGER NOT NULL,
	"name"	TEXT,
	"serial_num"	TEXT,
	"model"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
	FOREIGN KEY ("site_id") REFERENCES sites(id)
	FOREIGN KEY ("type_id") REFERENCES equipment_types(id)
);

INSERT INTO equipment_types (description, identifier)
	VALUES('cell router', 'R'),
		  ('cell sector', 'S'),
		  ('cell ptp', 'PTP'),
		  ('client ptmp', 'CPTMP'),
		  ('client ptp', 'CPTP');

INSERT INTO site_types (description, identifier)
	VALUES('cell', 'cell'),
		  ('gateway', 'gw'),
		  ('client', 'c');

INSERT INTO path_types (description, identifier)
	VALUES('backbone', 'BPTP'),
		  ('client ptmp', 'CPTMP'),
		  ('client ptp', 'CPTP');
