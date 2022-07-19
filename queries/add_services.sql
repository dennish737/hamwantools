DROP TABLE IF EXISTS "network_services";
CREATE TABLE IF NOT EXISTS "network_services" (
    "id" INTEGER NOT NULL,
    "org_id" INTEGER NOT NULL,
    "service_type" TEXT NO NULL,
    "service_name" TEXT NOT NULL,
    "service_ip" TEXT,
    FOREIGN KEY ("org_id") REFERENCES organizations("org_id")
    PRIMARY KEY("id" AUTOINCREMENT)

);




INSERT INTO network_services (org_id, service_type, service_name)
VALUES ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('spokane')), 'dns', 'dns_server_1'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('spokane')), 'dns', 'dns_server_2'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('spokane')), 'ntp', 'ntp_server_1'),
    ((SELECT org_id FROM organizations WHERE lower(club_name) = lower('spokane')), 'ntp', 'ntp_server_2');