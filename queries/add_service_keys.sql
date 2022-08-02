INSERT INTO services_pwd (org_id, site_id, tag, password)
VALUES
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'example_club'), NULL, 'wirelesskey', 'mykey'),
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'example_club'), NULL, 'backbonekey', 'mykey'),
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'example_club'), NULL, 'vrrpkey', 'mykey'),
    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'example_club'), NULL, 'ospfkey', 'mykey');
--    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'), NULL, 'wirelesskey', 'mykey'),
--    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'), NULL, 'backbonekey', 'mykey'),
--    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'), NULL, 'vrrpkey', 'mykey'),
--    ((SELECT x.org_id FROM organizations x WHERE lower(x.club_name) = 'spokane'), NULL, 'ospfkey', 'mykey');
