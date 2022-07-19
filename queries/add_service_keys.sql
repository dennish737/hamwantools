--
INSERT INTO services_pwd (org_id, tag, passwd)
VALUES ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('myclub')), 'wirelesskey', 'mykey'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('myclub')), 'backbonekey', 'mykey'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('myclub')), 'vrrpkey', 'mykey'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('myclub')), 'ospfkey', 'mykey'),

