"""Get list of IP address in a Network"""
import os
import subprocess
import ipaddress

FNULL = open(os.devnull, 'w')
IS_ON_POSIX = os.name == 'posix'
SHOW_MAC = False
USE_ARP = False

KNOWN_ARP_ERRORS_POSIX = ['-- no entry', '(incomplete)']
KNOWN_ARP_ERRORS_NT = ['No ARP Entries Found.']

def ip2bin(ip_addr):
    """Convert IP address to binary"""
    octets = map(int, ip_addr.split('/')[0].split('.'))
    binary = '{0:08b}{1:08b}{2:08b}{3:08b}'.format(*octets)
    range_bin = int(ip_addr.split('/')[1]) if '/' in ip_addr else None
    return binary[:range_bin] if range_bin else binary

def get_prefix(binary):
    """Get the Prefix of Subnet Mask"""
    prefix_count = 0
    for i in binary:
        if i == '1':
            prefix_count += 1
    return prefix_count

def get_ip_base():
    """Get list of IP in Network"""
    ip_addr = []
    subnet_mask = []
    if len(ip_addr) == 0:
        if IS_ON_POSIX:
            broadcast = []
            box = []
            ifconfig = subprocess.check_output('ifconfig').decode('ascii').splitlines()
            for i in ifconfig:
                if 'broadcast' in i:
                    broadcast = i.split('broadcast')[1].strip()
                    ip_addr.append('.'.join(broadcast.split('.')[:-1]) + '.0')
        else:
            ipconfig = subprocess.check_output('ipconfig').decode('ascii').splitlines()
            for i in ipconfig:
                if 'IPv4 Address' in i:
                    broadcast = i.split()[-1].strip()
                    ip_addr.append('.'.join(broadcast.split('.')[:-1]) + '.0')
                if 'Subnet Mask' in i:
                    box = i.split()[-1].strip()
                    subnet_mask.append(box)

    ip_base = []
    for i in range(len(subnet_mask)):
        prefixlen = str(get_prefix(ip2bin(subnet_mask[i])))
        ip_add = ip_addr[i]
        ip_base.append(ip_add + '/' + prefixlen)

    j = 0
    list_ip = []
    for i in range(len(ip_base)):
        list_ip.append(list(ipaddress.ip_network(ip_base[j]).hosts()))
        j = j+1

    for i in range(len(list_ip)):                   #Convert ip in list_ip to string
        for j in range(len(list_ip[i])):
            list_ip[i][j] = str(list_ip[i][j])

    return list_ip

if __name__ == '__main__':
    print(get_ip_base())
    