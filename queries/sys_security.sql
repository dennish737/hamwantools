-- list system information for site
SELECT s.name as site, se.name as sys_name, o.call_sign, np.timezone, np.log1, np.log2, np.dns1, np.dns2, np.ntp1, np.ntp2
FROM organizations o
INNER JOIN network_parameters np
ON np.org_id = o.org_id
INNER JOIN sites s
ON s.org_id = o.org_id
INNER JOIN site_equipment se
ON se.site_id = s.id
WHERE lower(s.name) = 'site1'
	AND o.org_id = (SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'example_club');


-- security
SELECT id, site_id, tag, password 
FROM services_pwd 
WHERE org_id = (SELECT x.org_id FROM organizations x WHERE lower(x.club_name) ='example_club')
	AND site_id = (SELECT y.id FROM sites y WHERE lower(y.name) = 'site1')
UNION ALL
SELECT  id, site_id, tag, password 
FROM services_pwd
WHERE org_id = (SELECT x.org_id FROM organizations x WHERE lower(x.club_name) ='example_club')
ORDER BY id DESC;

