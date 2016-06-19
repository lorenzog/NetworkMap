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

# those are required to catch GEXF files import errors
from xml.etree.cElementTree import ParseError as cParseError
from xml.etree.ElementTree import ParseError as ParseError

from errors import MyException
from netgrapher import grow_graph
from node import Node


logger = logging.getLogger('netgrapher')

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

SUPPORTED_FILE_FORMATS = [
    'GEXF',
    'DOT'
]
DEFAULT_FILE_FORMAT = 'GEXF'


# see: http://stackoverflow.com/a/37578709/204634
# but also: https://networkx.readthedocs.io/en/stable/reference/drawing.html#module-networkx.drawing.nx_agraph
def load_graph(savefile, file_format):
    """Does what it says on the tin(c)"""
    if os.path.exists(savefile):
        if file_format == 'GEXF':
            try:
                g = nx.read_gexf(savefile, node_type=Node)
            # I hate catching 'Exception' but read_gexf raises
            # 'cElementTree.ParseError' (or ElementTree.ParseError, no 'c')
            # which is nowhere to be found
            # except Exception as e:
            except (cParseError, ParseError) as e:
                raise MyException("Cannot read file {} using format {}: {}".format(
                    savefile, file_format, e))
        elif file_format == 'DOT':
            g = nx.nx_agraph.read_dot(savefile)
        else:
            raise MyException("Unknown file format {}".format(file_format))
    else:
        g = nx.Graph()
    return g


def save_graph(graph, savefile, file_format):
    """Does what it says on the tin(c)"""
    if os.path.exists(savefile):
        shutil.copy(savefile, "{}.bak".format(savefile))
        logger.info("Network DOT file backup saved: {}.bak".format(savefile))

    if file_format == 'GEXF':
        nx.write_gexf(graph, savefile)
    elif file_format == 'DOT':
        nx.nx_agraph.write_dot(graph, savefile)
    else:
        logger.error("Unknown file format requested")

    logger.info("Network file saved to {}".format(savefile))


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
    p.add_argument('-n', '--dry-run', action='store_true')

    # the dump file to load
    p.add_argument('dumpfile')
    # we'll try to guess, but can override
    p.add_argument(
        '-t', '--dumpfile-type',
        help="Dumpfile type; default: tries to guess based on file format.",
        choices=SUPPORTED_DUMPFILES)
    p.add_argument(
        '-o', '--dumpfile-os',
        help="Operating System; default: tries to guess.",
        choices=SUPPORTED_OS)
    p.add_argument(
        '-f', '--file-format', choices=SUPPORTED_FILE_FORMATS,
        default=DEFAULT_FILE_FORMAT)

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

    try:
        logger.debug("About to load file {}".format(savefile))
        loaded_graph = load_graph(savefile, args.file_format)
        logger.debug("Loaded graph:\nnodes\t{}\nedges\t{}".format(loaded_graph.nodes(), loaded_graph.edges()))
        final_graph = grow_graph(
            loaded_graph, args.dumpfile,
            dumpfile_os=args.dumpfile_os,
            dumpfile_type=args.dumpfile_type,
            ip=args.ip
        )
        if not args.dry_run:
            save_graph(final_graph, savefile, args.file_format)
        else:
            logger.info("Dry-run mode selected -not writing into savefile")
    except MyException as e:
        logger.error("Something went wrong: {}".format(e))
        raise SystemExit

    try:
        import pygraphviz as pgv
        # convert to image
        f = pgv.AGraph(savefile)
        f.layout(prog='circo')
        f.draw(DEFAULT_GRAPHIMG)
        logger.info("Output saved in {}".format(DEFAULT_GRAPHIMG))
    except ImportError as e:
        logger.debug("Cannot find pygraphviz.")
    except IOError as e:
        logger.error("Something went wrong when drawing, but the dot file is good. Try one of the graphviz programs manually")

    exit(0)


if __name__ == '__main__':
    main()
