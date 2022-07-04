-- An organization makes a request and receives an allocation from hamwan. We are assuming that an
-- organization can make multiple request for IP addresses, and receive non contiguous allocations,
-- of ip addresses.
--
-- Allocation are associated with an organization, and the org_id must be in hte organization vable
-- before the allocations can be added to the data base

-- example add location for spokane_club
INSERT INTO network_allocations (org_id, network_allocation, starting_address, ending_address, subnet_mask)
VALUES ((select org_id from organizations where club_name = 'spokane'),
    '44.12.128.0/21', '44.12.128.0', '44.12.135.255',21);