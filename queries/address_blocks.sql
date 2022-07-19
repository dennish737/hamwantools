-- script to view the address blocks

SELECT a.org_id, b.ip_address as network, c.ip_address as start_ip, d.ip_address as end_ip, e.ip_address as broadcast,
	a.num_ip, a.assigned
FROM address_blocks a
INNER JOIN ip_addresses b
ON b.id = a.network
INNER JOIN ip_addresses c
ON c.id = a.start_ip
INNER JOIN ip_addresses d
ON d.id = a.end_ip
INNER JOIN ip_addresses e
ON e.id = a.broadcast