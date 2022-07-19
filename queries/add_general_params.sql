-- script to add general parameters
INSERT INTO "general_params" (org_id, wireless_name, backbone_name, time_zone)
VALUES ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('myclub')), 'HamWan', 'HamWanB', 'America/Los_Angeles')