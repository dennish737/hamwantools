-- this script es an example of how list the path connection information

-- list all paths
SELECT a.name as "path", b.name as "site_a", d.name as "equip_a", c.name as "site_b", e.name as "equip_b"
FROM paths a
INNER JOIN sites b
ON b.id = a.site_a
INNER JOIN sites c
ON c.id = a.site_b
INNER JOIN site_equipment d
ON d.id = a.equip_a
INNER JOIN site_equipment e
ON e.id = a.equip_b;

-- select a specific path
SELECT a.name as "path", b.name as "site_a", d.name as "equip_a", c.name as "site_b", e.name as "equip_b"
FROM paths a
INNER JOIN sites b
ON b.id = a.site_a
INNER JOIN sites c
ON c.id = a.site_b
INNER JOIN site_equipment d
ON d.id = a.equip_a
INNER JOIN site_equipment e
ON e.id = a.equip_b
WHERE lower(a.name) = 'path1';
