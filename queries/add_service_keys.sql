--
BEGIN TRANSACTION;
INSERT INTO services_pwd (org_id, tag, passwd)
VALUES ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('spokane')), 'wirelesskey', 'mykey'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('spokane')), 'backbonekey', 'mykey'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('spokane')), 'vrrpkey', 'mykey'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('spokane')), 'ospfkey', 'mykey');

COMMIT;