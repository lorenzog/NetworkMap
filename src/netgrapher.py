#!/usr/bin/env python2.7
"""
POC of a network grapher
========================

Does stuff.

"""

import argparse
import logging
# import pprint
import os
import re
import shutil

import networkx as nx
import pygraphviz as pgv


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

DEFAULT_SAVEFILE = "networkmap.dot"
DEFAULT_GRAPHIMG = "/tmp/out.png"

# TODO add 'hosts' file for ip -> name support
SUPPORTED_DUMPFILES = [
    'arp',
    'route',
    'traceroute',
]
SUPPORTED_OS = [
    'windows'
]


# NOTE: do we really need networkx? Can we do everything with pygraphviz?
# https://github.com/pygraphviz/pygraphviz/blob/master/examples/simple.py
# mmh maybe not - networkx can help traversing the graphs, finding dupes, etc.

# using networkx:
# https://networkx.readthedocs.io/en/stable/reference/drawing.html#module-networkx.drawing.nx_agraph

class MyException(Exception):
    """Generic exception to handle program flow exits"""
    pass


# NOTE: what about 'ghost' IPs or multicast/broadcast?


class Node(object):
    def __init__(self, ip=None, mac=None):
        self.ip = ip
        self.mac = mac

    def __repr__(self):
        # FIXME should actually be a python expression able to generate
        # this same object i.e. Node(ip, mac)
        _ret = "Node IP: {}".format(self.ip)
        if self.mac:
            _ret += " [mac: {}]".format(self.mac)
        return _ret

    def __eq__(self, other):
        # if a mac address is defined,
        if self.mac and self.other.mac:
            return self.ip == self.other.ip and self.mac == self.other.mac

        # no mac address specified or one is undefined - we compare by IP
        return self.ip == self.other.ip


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
            m = re.match(r'  ([\w.]+)\s+(([0-9a-f]{2}-){5}[0-9a-f])', line)
            if m and len(m.groups()) >= 2:
                _node_ip = m.group(1)
                _node_mac = m.group(2)
                logger.debug("Found node {} with mac {}".format(_node_ip, _node_mac))
                nodes.append(Node(_node_ip, _node_mac))
                continue

    # centre node and neighbours
    return Node(_local_ip), nodes


def extract_from_arp(dumpfile, dumpfile_os, ip):
    """Given an arp dump, extracts IPs and adds them as nodes to the graph"""
    if dumpfile_os == 'windows':
        # local_net = parse_windows_arp(dumpfile, ip)
        centre_node, neighbours = parse_windows_arp(dumpfile, ip)
    else:
        # TODO write parser for linux
        raise NotImplementedError("Sorry dude")

    g = nx.Graph()
    # centre node
    centre = Node(centre_node)
    for node in neighbours:
        g.add_edge(centre, node, source="arp")

    logger.debug("Local graph:\nnodes\t{}\nedges\t{}".format(g.nodes(), g.edges()))
    return g


def extract_from_route(dumpfile, dumpfile_os, ip):
    raise NotImplementedError("Sorry, haven't written this yet")


def extract_from_tr(dumpfile, dumpfile_os, ip):
    # NOTE
    # here each hop can be a new node, with an edge connecting back towards `ip`
    raise NotImplementedError("Sorry, haven't written this yet")


def guess_dumpfile_type(f):
    # TODO read the first few lines of the file and guess the dumpfile
    pass


def guess_dumpfile_os(f):
    # TODO read the first few lines of the file and guess the OS
    pass


def grow_graph(loaded_graph, dumpfile, dumpfile_os=None, dumpfile_type=None, ip=None):
    """Given a bunch of nodes, if they are not dupes add to graph"""

    if dumpfile_type is None:
        dumpfile_type = guess_dumpfile_type(dumpfile)
    if dumpfile_os is None:
        dumpfile_os = guess_dumpfile_os(dumpfile)

    logger.debug("Dumpfile: {}, OS: {}".format(dumpfile_type, dumpfile_os))

    if dumpfile_type not in SUPPORTED_DUMPFILES:
        raise MyException("Invalid dumpfile type")
    if dumpfile_os not in SUPPORTED_OS:
        raise MyException("Invalid OS")

    if dumpfile_type == 'arp':
        new_graph = extract_from_arp(dumpfile, dumpfile_os, ip)
    elif dumpfile_type == 'route':
        new_graph = extract_from_route(dumpfile, dumpfile_os, ip)
    elif dumpfile_type == 'traceroute':
        new_graph = extract_from_tr(dumpfile, dumpfile_os, ip)
    else:
        # this bubbles to the user for now
        raise NotImplementedError("This dumpfile is not supported.")

    # NOTE:
    # 1. arp tables give immediate neighbours so can add an edge.
    # 2. routes can give hosts that are not immediately adjacent. In this case,
    # they should not be added as direct edges when growing the graph.
    # 3. traceroutes show paths (i.e. direct edges)
    final_graph = nx.union(loaded_graph, new_graph)
    return final_graph


# see: http://stackoverflow.com/a/37578709/204634
# but also: https://networkx.readthedocs.io/en/stable/reference/drawing.html#module-networkx.drawing.nx_agraph
def load_graph(savefile):
    """Does what it says on the tin(c)"""
    if os.path.exists(savefile):
        g = nx.nx_agraph.read_dot(savefile)
    else:
        g = nx.Graph()
    return g


def save_graph(graph, savefile, force):
    """Does what it says on the tin(c)"""
    if os.path.exists(savefile) and not force:
        shutil.copy(savefile, "{}.bak".format(savefile))
        logger.info("Network DOT file backup saved: {}.bak".format(savefile))
    nx.nx_agraph.write_dot(graph, savefile)
    logger.info("Network DOT file saved to {}".format(savefile))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-d', '--debug', action='store_true')

    p.add_argument(
        '-i', '--ip',
        help=("The IP address where the dumpfile was taken. "
              "Default: tries to guess bsaed on the content of the file")
    )

    p.add_argument(
        '-s', '--savefile',
        help="Use this file to store information. Creates it if it does not exist.",
        default=DEFAULT_SAVEFILE
    )
    p.add_argument(
        '-f', '--force', action='store_true',
        help="Overwrites the savefile"
    )
    p.add_argument('-n', '--dry-run', action='store_true')

    # the dump file to load
    p.add_argument('dumpfile')
    # we'll try to guess, but can override
    p.add_argument(
        '-t', '--dumpfile-type',
        help="Dumpfile type; default: tries to guess based on file format.",
        choices=SUPPORTED_DUMPFILES
    )
    p.add_argument(
        '-o', '--dumpfile-os',
        help="Operating System; default: tries to guess.",
        choices=SUPPORTED_OS
    )

    args = p.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    savefile = args.savefile
    if not os.path.exists(args.dumpfile):
        raise SystemExit("File {} does not exist".format(args.dumpfile))

    #
    # Boilerplate ends
    ###

    loaded_graph = load_graph(savefile)
    logger.debug("Loaded graph:\nnodes\t{}\nedges\t{}".format(loaded_graph.nodes(), loaded_graph.edges()))
    try:
        final_graph = grow_graph(
            loaded_graph, args.dumpfile,
            dumpfile_os=args.dumpfile_os,
            dumpfile_type=args.dumpfile_type,
            ip=args.ip
        )
        if not args.dry_run:
            save_graph(final_graph, savefile, args.force)
        else:
            logger.info("Dry-run mode selected -not writing into savefile")
    except MyException as e:
        logger.error("Something went wrong: {}".format(e))
        raise SystemExit

    # convert to image
    f = pgv.AGraph(savefile)
    f.layout(prog='circo')
    f.draw(DEFAULT_GRAPHIMG)
    logger.info("Output saved in {}".format(DEFAULT_GRAPHIMG))

    exit(0)


if __name__ == '__main__':
    main()
