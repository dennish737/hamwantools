-- several tables contain "type" information which is used to identify
-- a class of something. This file initializes the type tables.
-- Note this only need t obe done once.
-- Uses can add additional types to the table directly
--
-- Version 1.0.0
--
--DELETE FROM equipment_groups;
--UPDATE sqlite_sequence SET seq = 0 WHERE name = 'equipment_groups';
INSERT INTO equipment_groups (group_name, description, suffix, interface_list)
	VALUES('router', 'cell router','r','{"ether":["ether1"], "vrrp":["vrrp1"], "dhcp":["pool1"]}'),
		  ('sector', 'cell sector router','s', '{"ether":["ether1"], "wlan":["wlan1"], "vrrp":["vrrp1"], "dhcp":["pool1", "pool2"]}'),
		  ('bptp', 'cell ptp router','ptp', '{"ether":["ether1"], "wlan":["wlan1"],"vrrp":["vrrp1"]}'),
		  ('cptmp', 'client ptmp connection','cptmp','{"ether":["ether1"], "wlan":["wlan1"]}'),
		  ('cptp', 'client ptp connection','cptp','{"ether":["ether1"], "wlan":["wlan1"]}'),
		  ('gateway', 'cell gateway router', 'gw', '{"ether":["ether1"], "vrrp":["vrrp1"]}'),
		  ('default_gateway', 'system default gateway', 'dgw', '{"vrrp":["vrrp1"]}');

--DELETE FROM site_types;
--UPDATE sqlite_sequence SET seq = 0 WHERE name = 'site_types';
INSERT INTO site_types (description, identifier)
	VALUES('cell', 'cell'),
		  ('gateway', 'gw'),
		  ('client', 'c');

--DELETE FROM path_types;
--UPDATE sqlite_sequence SET seq = 0 WHERE name = 'path_types';
INSERT INTO path_types (description, identifier)
	VALUES('backbone', 'BPTP'),
		  ('client ptmp', 'CPTMP'),
		  ('client ptp', 'CPTP');

--DELETE FROM ip_types;
--UPDATE sqlite_sequence SET seq = 0 WHERE name = 'ip_types';
INSERT INTO ip_types (type_name)
VALUES ("pool"), ("ptp"), ("device");

--DELETE FROM community_types;
--UPDATE sqlite_sequence SET seq = 0 WHERE name = 'community_types';
INSERT INTO "community_types" ("name")
VALUES ("public"),("private"),("trap");

-- name substitutions: these are simple test substitutions primarily
-- used for interface names allowing for multiple interfaces of the same type
-- for a device
INSERT OR IGNORE INTO "string_substitutes" (template_name, dict_name)
VALUES ('ETHER1', 'ether1'),
	('ETHER2', 'ether2'),
	('ETHER3', 'ether3'),
	('ETHER4', 'ether4'),
	('ETHER5', 'ether5'),
	('ETHER6', 'ether6'),
	('ETHER7', 'ether7'),
	('ETHER8', 'ether8'),
	('WLAN1', 'wlan1'),
	('WLAN2', 'wlan2'),
	('WLAN3', 'wlan3'),
	('WLAN4', 'wlan4'),
	('DHCP1', 'dhcp1'),
	('DHCP2', 'dhcp2'),
	('DHCP3', 'dhcp3'),
	('DHCP4', 'dhcp4'),
	('VRRP1', 'vrrp1'),
	('VRRP2', 'vrrp2'),
	('VRRP3', 'vrrp3'),
	('VRRP4', 'vrrp4');

COMMIT;