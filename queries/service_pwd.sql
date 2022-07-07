-- common requires passwords
-- At a minimum you need a password wireless networks and virtual routing (vrrp) device
-- The planner should update the names and the passwords before running the script
INSERT INTo passwords (name, password)
VALUES	("backbone_ssid","bssid_name", "password"),
		("client_ssid","cssid_name","password"),
		("vrrp","vrrp_name","password");