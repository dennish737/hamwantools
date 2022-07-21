-- several tables contain "type" information which is used to identify
-- a class of something. This file initializes the type tables.
-- Note this only need t obe done once.
-- Uses can add additional types to the table directly
--
-- Version 1.0.0
--

INSERT OR IGNORE INTO equipment_groups (group_name, description, suffix, interface_list)
	VALUES('router', 'router','R','{"ether":["ether1", "ether2"], "vrrp":["vrrp1"]}'),
		  ('sector', 'sector','S', '{"ether":["ether1"], "wlan":["wlan1"], "vrrp":["vrrp1"]}'),
		  ('bptp', 'backbone ptp connection','PTP', '{"ether":["ether1"], "wlan":["wlan1"],"vrrp":["vrrp1"]}'),
		  ('cptp', 'client ptp connection','CPTP','{"ether":["ether1"], "wlan":["wlan1"], "vrrp":["vrrp1"]}'),
		  ('gateway', 'cell gateway router', 'GW', '{"ether":["ether1"], "wlan":["wlan1"], "vrrp":["vrrp1"]}'),
		  ('default_gateway', 'system default gateway', 'DGW', '{"vrrp":["vrrp1"]}');

INSERT OR IGNORE INTO site_types (description, identifier)
	VALUES('cell', 'cell'),
		  ('gateway', 'gw'),
		  ('client', 'c');

INSERT OR IGNORE INTO path_types (description, identifier)
	VALUES('backbone', 'BPTP'),
		  ('client ptmp', 'CPTMP'),
		  ('client ptp', 'CPTP');

INSERT OR IGNORE INTO ip_types (type_name)
VALUES ("pool"), ("ptp"), ("device");

-- Configuration Files

COMMIT;