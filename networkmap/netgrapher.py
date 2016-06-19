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

import networkx as nx

import parsers
from errors import MyException


logger = logging.getLogger('netgrapher')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

DEFAULT_SAVEFILE = "networkmap.dot"
DEFAULT_GRAPHIMG = "/tmp/out.png"

# using networkx:
# https://networkx.readthedocs.io/en/stable/reference/drawing.html#module-networkx.drawing.nx_agraph


def extract_from_arp(dumpfile, dumpfile_os, ip):
    """Given an arp dump, extracts IPs and adds them as nodes to the graph"""
    if dumpfile_os == 'windows':
        centre_node, neighbours = parsers.parse_windows_arp(dumpfile, ip)
    elif dumpfile_os == 'linux':
        centre_node, neighbours = parsers.parse_linux_arp(dumpfile, ip)
    else:
        raise NotImplementedError("Sorry, haven't written this yet")

    g = nx.Graph()
    for node in neighbours:
        g.add_edge(centre_node, node, source="arp")

    logger.debug("Local graph:\nnodes\t{}\nedges\t{}".format(g.nodes(), g.edges()))
    return g


def extract_from_route(dumpfile, dumpfile_os, ip):
    # TODO

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


def grow_graph(loaded_graph, dumpfile, dumpfile_os=None, dumpfile_type=None, ip=None):
    """Given a bunch of nodes, if they are not dupes add to graph"""

    if dumpfile_type is None or dumpfile_os is None:
        # have to open the file for reading once anyway
        guessed_type, guessed_os = parsers.guess_dumpfile_type_and_os(dumpfile)
        logger.info("Guessed file type: {}, OS: {}".format(guessed_type, guessed_os))

    # decide whether to use the guess or the specified dumpfile type
    if dumpfile_type is None:
        if guessed_type is None:
            raise MyException("Cannot guess file type. Please specify it manually.")
        else:
            dumpfile_type = guessed_type
    else:
        if guessed_type is not None and dumpfile_type != guessed_type:
            logger.warn("Guessed type does not match specified type. Ignoring guess.")

    # same for the OS
    if dumpfile_os is None:
        if guessed_os is None:
            raise MyException("Cannot guess OS. Please specify it manually.")
        else:
            dumpfile_os = guessed_os
    else:
        if guessed_os is not None and dumpfile_os != guessed_os:
            logger.warn("Guessed type does not match specified type. Ignoring guess.")

    logger.debug("Dumpfile: {}, OS: {}".format(dumpfile_type, dumpfile_os))

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
