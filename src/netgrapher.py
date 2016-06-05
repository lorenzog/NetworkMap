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
import shutil

import networkx as nx
import pygraphviz as pgv

import parsers
from errors import MyException


logger = logging.getLogger('netgrapher')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

DEFAULT_SAVEFILE = "networkmap.dot"
DEFAULT_GRAPHIMG = "/tmp/out.png"

# TODO add nmap support for host type
# TODO add 'hosts' file for ip -> name support
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


# NOTE: do we really need networkx? Can we do everything with pygraphviz?
# https://github.com/pygraphviz/pygraphviz/blob/master/examples/simple.py
# mmh maybe not - networkx can help traversing the graphs, finding dupes, etc.

# using networkx:
# https://networkx.readthedocs.io/en/stable/reference/drawing.html#module-networkx.drawing.nx_agraph

# NOTE: what about 'ghost' IPs or multicast/broadcast?


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

    # TODO this can be a list, for multiple interfaces. That makes it fun to implement..
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

    try:
        # convert to image
        f = pgv.AGraph(savefile)
        f.layout(prog='circo')
        f.draw(DEFAULT_GRAPHIMG)
        logger.info("Output saved in {}".format(DEFAULT_GRAPHIMG))
    except IOError as e:
        logger.error("Something went wrong when drawing, but the dot file is good. Try one of the graphviz programs manually")

    exit(0)


if __name__ == '__main__':
    main()
