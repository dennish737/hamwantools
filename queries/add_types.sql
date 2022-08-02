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
	VALUES('router', 'cell router','r','{"ether":["ether1"], "vrrp":["vrrp1"], "dhcp":["block0"]}'),
		  ('sector', 'cell sector router','s', '{"ether":["ether1"], "wlan":["wlan1"], "vrrp":["vrrp1"], "dhcp":["block0", "block1"]}'),
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

COMMIT;