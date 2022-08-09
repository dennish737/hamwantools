
INSERT INTO global_parameters (org_id, site_id, timezone, log1, log2, dns1, dns2, ntp1, ntp2)
VALUES ((SELECT org_id FROM organizations WHERE lower(club_nme) = 'spokane'), NULL, 'America/Los Angles',
		NULL, NULL, '8.8.8.8', '8.8.4.4', 44.12.128.0, 44.12.128.0);
