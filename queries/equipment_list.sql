-- example script to list equipment
SELECT  b.name as site , a.name as "equipment"
FROM site_equipment  a
INNER JOIN sites b
ON b.id = a.site_id
ORDER BY b.name;


-- equipment for s specific site
SELECT b.name as site , a.name as "equipment"
FROM site_equipment  a
INNER JOIN sites b
ON b.id = a.site_id
WHERE a.site_id = (SELECT x.id FROM sites x WHERE lower(x.name) = 'site1');

-- list all ptp routers for all sites
SELECT  b.name as site , a.name as "equipment"
FROM site_equipment  a
INNER JOIN sites b
ON b.id = a.site_id
WHERE a.group_id = (SELECT x.id FROM equipment_groups x WHERE (x.suffix) = 'PTP');


-- count the number of ptp routers on eac site
SELECT  b.name as site , count(a.name) as "number"
FROM site_equipment  a
INNER JOIN sites b
ON b.id = a.site_id
WHERE a.group_id = (SELECT x.id FROM equipment_groups x WHERE (x.suffix) = 'PTP')
GROUP BY b.name;

-- list all un assigned ptp routers for all sites ordered by site
SELECT  b.name as site , a.name as "equipment"
FROM site_equipment  a
INNER JOIN sites b
ON b.id = a.site_id
WHERE a.active = 0 AND a.group_id = (SELECT x.id FROM equipment_groups x WHERE (x.suffix) = 'PTP')
ORDER BY b.name;