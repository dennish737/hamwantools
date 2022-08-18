INSERT INTO services_pwd (org_id, site_id, tag, password)
VALUES
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'), NULL, 'vrrp_key', 'mykey'),
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'), NULL, 'ospf_key', 'mykey');

INSERT INTO ptp_security (org_id, path_id, SSID, passwd)
VALUES
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'), NULL, 'WAConnect', 'mykey'),
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'),
        (SELECT y.id FROM paths y WHERE lower(y.name) = 'path2'), 'SPODEM', 'mykey'),
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'),
        (SELECT y.id FROM paths y WHERE lower(y.name) = 'path4'), 'SPODEM', 'mykey');

INSERT INTO client_security(org_id, site_id, SSID, passwd)
VALUES
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'), NULL, 'WAConnect', 'mykey');
