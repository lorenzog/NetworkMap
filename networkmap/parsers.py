import logging
import re

# from node import Node
from errors import MyException


# XXX this has to be the same name as the logger object in
# netgrapher.py...
logger = logging.getLogger('netgrapher')

# NOTE there can be more than one way of matching; the regexps are applied to
# all lines of the file until a match is found
guess_data = (
    (('arp', 'windows'), r'^Interface:\s+'),
    (('arp', 'linux'), r'^Address\s+HWtype\s+HWaddress\s+Flags\s+Mask\s+Iface$'),
    (('arp', 'openbsd'), r'^Host\s+Ethernet\sAddress\s+Netif\sExpire\sFlags$'),
    #
    (('traceroute', 'linux'), r'^traceroute to .+ \([\d.]+\), \d+ hops max, \d+ byte packets$'),
    # doubled, just because
    (('route', 'linux'), r'^Kernel IP routing table$'),
    (('route', 'linux'), r'^Destination\s+Gateway\s+Genmask\s+Flags\sMetric\sRef\s+Use\sIface$'),
    (('route', 'windows'), r'===========================================================================')
)

# build separate lists for the help menu
SUPPORTED_DUMPFILES = set(a[0] for a, b in guess_data)
SUPPORTED_OS = set(a[1] for a, b in guess_data)


# XXX perhaps this could be extended by using more than one regexp to match
# across lines? Maybe using a defaultDict with a list of regexps instead of tuples
def guess_dumpfile_type_and_os(dumpfile):
    """Returns file_type, os when any line of the input file matches the regexp"""
    with open(dumpfile) as f:
        # read every line exactly once
        for line in f.readlines():
            logger.debug("line:\n{}".format(line))
            # ...and try to match it against a known os/type tuple
            for type_os, regexp in guess_data:
                m = re.match(regexp, line)
                if m:
                    # got match
                    file_type, os = type_os
                    logger.debug("Match: {}, {}".format(file_type, os))
                    return file_type, os
                logger.debug("No match for {}".format(type_os))

    return None, None


def parse_linux_tr(dumpfile, ip):
    hops = []
    if ip is None:
        raise MyException("Linux ARP does not contain the IP of the "
                          "centre node; please supply it manually with --ip\n")
    hops.append(ip)
    with open(dumpfile) as f:
        for line in f.readlines():
            # 1  10.137.4.1  0.550 ms  0.463 ms  0.383 ms
            m = re.match(r'\s+\d+\s+([\w.]+)', line)
            if m and len(m.groups()) >= 1:
                _hop_ip = m.group(1)
                logger.debug("Found hop: {}".format(_hop_ip))
                hops.append(_hop_ip)
    return hops


def parse_linux_arp(dumpfile):
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
                nodes.append((_node_ip, _node_mac))
                continue
    return nodes


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
                nodes.append((_node_ip, _node_mac))
                continue

    # centre node and neighbours
    return _local_ip, nodes


def parse_linux_route(dumpfile):
    # NOTE from 'route' man page:
    #       Flags  Possible flags include
    #           U (route is up)
    #           H (target is a host)
    #           G (use gateway)
    #           R (reinstate route for dynamic routing)
    #           D (dynamically installed by daemon or redirect)
    #           M (modified from routing daemon or redirect)
    #           A (installed by addrconf)
    #           C (cache entry)
    #           !  (reject route)
    host_routes = []
    network_routes = []
    default_routes = []

    with open(dumpfile) as f:
        for line in f.readlines():
            # skip first line
            m = re.match(r'Kernel IP routing table', line)
            if m is not None:
                continue
            # skip second line
            m = re.match(r"Destination\s+Gateway\s+Genmask", line)
            if m is not None:
                continue

            # regexp to match an IP: ([\w.]+)
            # Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
            # 0.0.0.0         10.137.4.1      0.0.0.0         UG    0      0        0 eth0
            m = re.match(r'(?P<dest>[\w.]+)\s+(?P<gw>[\w.]+)\s+(?P<mask>[\w.]+)\s+(?P<flags>[\w.]+)', line)
            if m is not None:
                _dest = m.group('dest')
                _gw = m.group('gw')
                _mask = m.group('mask')
                _flags = m.group('flags')

                if _flags[0] != 'U':
                    logger.debug("Route {} is not up; skipping...".format(line))

                # basic example, I'm sure it breaks in the face of some complex scenario
                if _dest == '0.0.0.0':
                    logger.debug("Adding default gateway: {}".format(_dest))
                    default_routes.append(_gw)
                    # next line baby
                    continue

                if 'H' in _flags:
                    # it's a host route
                    _hr = (_dest, _mask, _gw)
                    logger.debug("Adding host route: {}".format(_hr))
                    host_routes.append(_hr)
                    continue

                # what's left must be a network route
                # TODO bar the odd cases like ! -- see notes on top of function
                _nr = (_dest, _mask, _gw)
                logger.debug("Adding network route: {}".format(_nr))
                network_routes.append(_nr)

    # host and network routes have the form: (destination, netmask, gateway)
    return host_routes, network_routes, default_routes
