#!/usr/bin/env python2.7
"""
POC of a network grapher
========================

Does stuff.


"""
# TODO add nmap support for host type
# TODO add 'hosts' file for ip -> name support
# NOTE: what about 'ghost' IPs or multicast/broadcast?
# TODO add support for multi-interface

import logging
# import pprint

import networkx as nx

import parsers
from errors import MyException


logger = logging.getLogger('netgrapher')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

DEFAULT_SAVEFILE = "networkmap.dot"
DEFAULT_GRAPHIMG = "/tmp/out.png"

SUPPORTED_DUMPFILES = [
    'arp',
    'route',
    'traceroute',
]

SUPPORTED_OS = [
    'windows',
    'linux',
    'openbsd'
]


# using networkx:
# https://networkx.readthedocs.io/en/stable/reference/drawing.html#module-networkx.drawing.nx_agraph


def extract_from_arp(dumpfile, dumpfile_os, ip):
    """Given an arp dump, extracts IPs and adds them as nodes to the graph"""
    if dumpfile_os == 'windows':
        centre_node, neighbours = parsers.parse_windows_arp(dumpfile, ip)
    elif dumpfile_os == 'linux':
        centre_node, neighbours = parsers.parse_linux_arp(dumpfile, ip)
    else:
        raise NotImplementedError("Sorry dude")

    g = nx.Graph()
    for node in neighbours:
        g.add_edge(centre_node, node, source="arp")

    logger.debug("Local graph:\nnodes\t{}\nedges\t{}".format(g.nodes(), g.edges()))
    return g


def extract_from_route(dumpfile, dumpfile_os, ip):
    # TODO
    raise NotImplementedError("Sorry, haven't written this yet")


def extract_from_tr(dumpfile, dumpfile_os, ip):
    # NOTE
    # here each hop can be a new node, with an edge connecting back towards `ip`
    if dumpfile_os == 'linux':
        # returns an (ordered!) list of nodes, where the first is the centre node
        hops = parsers.parse_linux_tr(dumpfile, ip)
    else:
        raise NotImplementedError("Sorry, haven't written this yet")

    g = nx.Graph()
    if len(hops) == 0:
        logger.info("No hops found in traceroute file")
        return g

    # link each node with the preceding one
    for hopno, node in enumerate(hops[1:]):
        g.add_edge(hops[hopno], node, source="traceroute")

    return g


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
