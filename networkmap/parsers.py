import logging
import re

from node import Node
from errors import MyException


# XXX this has to be the same name as he logger object in
# netgrapher.py...
logger = logging.getLogger('netgrapher')


def parse_linux_tr(dumpfile, ip):
    hops = []
    if ip is None:
        raise MyException("Linux ARP does not contain the IP of the "
                          "centre node; please supply it manually\n")
    hops.append(Node(ip))
    with open(dumpfile) as f:
        for line in f.readlines():
            # 1  10.137.4.1  0.550 ms  0.463 ms  0.383 ms
            m = re.match(r'\s+\d+\s+([\w.]+)', line)
            if m and len(m.groups()) >= 1:
                _hop_ip = m.group(1)
                logger.debug("Found hop: {}".format(_hop_ip))
                hops.append(Node(_hop_ip))
    return hops


def parse_linux_arp(dumpfile, ip):
    nodes = []
    with open(dumpfile) as f:
        for line in f.readlines():
            # Address HWtype HWaddress Flags Mask Iface
            # 10.137.1.8 ether 00:16:3e:5e:6c:06 C vif2.0
            # similar regexp than the windows arp, except it uses : instead of -
            m = re.match(r'([\w.]+)\s+\w+\s+(([0-9a-f]{2}:){5}[0-9a-f]{2})', line)
            if m and len(m.groups()) >= 2:
                _node_ip = m.group(1)
                _node_mac = m.group(2)
                logger.debug("Found node {} with mac {}".format(_node_ip, _node_mac))
                nodes.append(Node(_node_ip, _node_mac))
                continue
    if ip is None:
        raise MyException("Linux ARP does not contain the IP of the "
                          "centre node; please supply it manually\n")
    return Node(ip), nodes


def parse_windows_arp(dumpfile, ip):
    """Windows ARP file parsing"""
    nodes = []
    with open(dumpfile) as f:
        for line in f.readlines():
            # the first line looks like:
            # Interface: 10.137.2.16 --- 0x11
            m = re.match(r'Interface: (.+) ---', line)
            if m and len(m.groups()) >= 1:
                _local_ip = m.group(1)
                logger.debug("Found centre node: {}".format(_local_ip))
                if ip is not None and _local_ip != ip:
                    raise MyException(
                        "The IP found in the ARP file is {} but "
                        "you supplied {}. Aborting...".format(
                            _local_ip, ip)
                    )
                continue

            # lines with IPs and MAC addresses look like:
            #   10.137.2.1            fe-ff-ff-ff-ff-ff     dynamic
            # regexp to match an IP: ([\w.]+)
            # regexp to match a mac: (([0-9a-f]{2}-){5}[0-9a-f])
            # start with two empty spaces,
            m = re.match(r'  ([\w.]+)\s+(([0-9a-f]{2}-){5}[0-9a-f]{2})', line)
            if m and len(m.groups()) >= 2:
                _node_ip = m.group(1)
                _node_mac = m.group(2)
                logger.debug("Found node {} with mac {}".format(_node_ip, _node_mac))
                nodes.append(Node(_node_ip, _node_mac))
                continue

    # centre node and neighbours
    return Node(_local_ip), nodes
