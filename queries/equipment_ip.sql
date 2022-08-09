SELECT eq.*, ip.ip_address FROM site_equipment eq
INNER JOIN interfaces if
ON if.equip_id = eq.id
INNER JOIN ip_addresses ip
ON if.addr_id = ip.id
WHERE group_id = (SELECT x.id FROM equipment_groups x WHERE x.group_name = "sector") AND
	if.if_name = 'ether1';
	