import ipaddress

def ip2long(ip_addr):
    return int(ipaddress.ip_address(ip_addr))

def ip2hex(ip_addr):
    return hex(int(ipaddress.ip_address(ip_addr)))

def int2ip( i):
    return str(ipaddress.ip_address(i))

def hex2ip(hex_val):
    i = int(hex_val, 16)
    return str(ipaddress.ip_address(i))
