select network_allocation,
	wirelessname, wirelesskey,
	backbonename, backbonekey,
	defaultgateway, vrrpkey,
	log_server,
	dns_server1,
	dns_server2,
	ntp_server1,
	ntp_server2,
	timezone
from regions
where regionid = 9;