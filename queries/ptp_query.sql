select a.sys_name, a._from, a._to, a.routername as ROUTERNAME, a.wanip as ROUTERWANIP,
	a.netaddress as NETWORKIP, c.etherip as ROUTERETHERIP,
	b.routername as REMOTENAME, b.wanip as REMOTEROUTERIP
from ptprouters a
inner join ptprouters b
on b._to = a._from and b._from = a._to
inner join routers c
on c.sys_name = a.sys_name
order by a._from
;