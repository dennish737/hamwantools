-- The organization is the 'club' setting up the ham wan network.
-- The data base will allow for multiple organization to be added
-- to the data set.
-- Sites, paths, ip addresses, etc., are all segmented by the organization
--
-- Version 1.0.0
--
-- When added an org id is created for the organization, which is used by other
-- components. To access the organization id, we can use the club name. Because
-- of this the club name must be unique.

-- The example script only includes the minimum fields to create the
--  organization, but additional fields can be provided.
--
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

INSERT INTO organizations (club_name,club_contact,friendly_name,state,county,state_region_id,ptp_net_size,
    device_net_size,block_size,share_ptp_net)
VALUES ('example_club','somebody','MyClub','MyState','Some_where',NULL,256,256,16,0)
--VALUES ('spokane','somebody','Spokane','Washington','Spokane',NULL,256,256,16,0);
COMMIT;