SELECT p.name, spa.name as site_a, spb.name as site_b, pt.identifier as type_id, spa.name as device_a, spb.name as device_b
FROM paths p
INNER JOIN sites sa
ON sa.id = p.site_a
INNER JOIN sites sb
ON sb.id = p.site_b
INNER JOIN path_types pt
ON pt.id = p.type_id
INNER JOIN site_equipment spa
ON spa.id = p.device_a
INNER JOIN site_equipment spb
ON spb.id = p.device_b
WHERE p.org_id = (SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'example_club');