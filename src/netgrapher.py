#!/usr/bin/env python2.7
"""
POC of a network grapher
========================

"""

import argparse
import logging
import os


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

DEFAULT_SAVEFILE = "networkmap.xml.gz"
SUPPORTED_DUMPFILES = [
    'arp',
    'route',
    'traceroute',
]


def grow_graph(current_graph, dumpfile, dumpfile_type):
    """Given a bunch of nodes, if they are not dupes add to graph"""

    # TODO
    # guess the dumpfile based on structure, or use type if provided
    # extract nodes by IP

    # TODO find the ip of the current node, or 'centre' of this view
    # Maybe a dictionary like this?
    # { 'current_ip': [
    #       list of nodes, ...
    #   ]
    # }
    # then make a new graph object

    # NOTE:
    # 1. arp tables give immediate neighbours so can add an edge.
    # 2. routes can give hosts that are not immediately adjacent. In this case,
    # they should not be added as direct edges when growing the graph.
    # 3. traceroutes show paths (i.e. direct edges)

    # TODO
    # then grow the existing graph (if any in the file) with the latest 'view'
    # from the dumpfile

    pass


# see: http://stackoverflow.com/a/37578709/204634
def load_graph(savefile):
    """Does what it says on the tin(c)"""
    # return graph
    pass


def save_graph(graph, savefile, force):
    """Does what it says on the tin(c)"""
    pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-d', '--debug', action='store_true')

    p.add_argument(
        '-s', '--savefile',
        help="Use this file to store information. Creates it if it does not exist.",
        default=DEFAULT_SAVEFILE
    )
    p.add_argument(
        '-f', '--force', action='store_true',
        help="Overwrites the savefile"
    )

    # the dump file to load
    p.add_argument('dumpfile')
    # we'll try to guess, but can override
    p.add_argument(
        '-t', '--dumpfile-type',
        help="Dumpfile type; default: tries to guess based on file format.",
        choices=SUPPORTED_DUMPFILES
    )

    args = p.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    savefile = args.savefile
    # default: create a new savefile
    if not os.path.exists(savefile):
        logger.debug("No savefile found {}. Will create a new one".format(savefile))
    else:
        if args.force:
            logger.debug("Overwriting savefile {}".format(savefile))
        else:
            # if the file already exist, don't overwrite but assume we're adding to it.
            logger.info("Savefile {} already existing; appending to it".format(savefile))

    if not os.path.exists(args.dumpfile):
        raise SystemError("File {} does not exist".format(args.dumpfile))

    graph = load_graph(savefile)
    grow_graph(graph, args.dumpfile, args.dumpfile_type)
    save_graph(graph, savefile, args.force)

    exit(0)


if __name__ == '__main__':
    main()
