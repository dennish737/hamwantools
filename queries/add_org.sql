-- the organization is the 'club' setting up the ham wan network.
-- when added an org id is created for the organization. To access the
-- organization we can use the club name. Because of this the club
-- name must be unique

-- The following items, for an organization, can be defined by the user:
-- 1) state -> optional
-- 2) county -> optional
-- 3) state_region_id -> optional
-- 4) friendly -> optional
-- 5) club name -> required, the official club name
-- 6) club_contact -> optional, club contact information
-- 7) ptp_net_size -> default 256
-- 8) device_net_size -> default 256
-- 9) block_size -> default 16, the number of ip addresses in each block
-- 10) share_ptp_net -> default 0 : do not share

-- example script to add an organization
INSERT INTO organizations (state,county,state_region_id, friendly_name, club_name )
VALUES ('Washington','Spokane', 9, 'Spokane', 'spokane_club' );