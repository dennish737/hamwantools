-- list of ptp connections for site
SELECT s.name as site_name, se.name as equipment_name, 
	if.if_name as interface_name, ip.ip_address,
	CASE if.if_type 
	WHEN 'wlan'
		THEN (SELECT r.ip_address FROM ip_addresses r WHERE r.reserved = ip.reserved AND r.assigned != ip.assigned
			AND r.ip_type = (SELECT z.id FROM ip_types z WHERE lower(z.type_name) = 'ptp'))
	ELSE NULL 
	END as remote_ip
FROM sites s
INNER JOIN site_equipment se
ON  se.site_id = s.id
INNER JOIN interfaces if
ON if.equip_id = se.id
INNER JOIN ip_addresses ip
ON ip.id = if.addr_id
WHERE s.org_id = (SELECT x.org_id FROM organizations x WHERE lower(club_name) = 'example_club')
	AND lower(s.name) = 'site1'
	AND se.group_id = (SELECT y.id FROM equipment_groups y WHERE lower(y.group_name) = 'bptp')
	



