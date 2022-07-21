



BEGIN;
INSERT INTO network_services (org_id, service_type, service_name)
VALUES ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('example_club')), 'dns', 'dns_server_1'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('example_club')), 'dns', 'dns_server_2'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('example_club')), 'ntp', 'ntp_server_1'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('example_club')), 'ntp', 'ntp_server_2');
COMMIT;