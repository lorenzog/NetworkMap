#!/usr/bin/env python2.7
"""
POC of python parser
====================

"""

import argparse
import logging
import os


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

DEFAULT_SAVEFILE = "networkmap.xml.gz"
SUPPORTED_DUMPFILES = [
    'route',
    'arp',
]


def load_graph(savefile):
    # return graph
    pass


def load_dump(dumpfile, dumpfile_type):
    # TODO
    # guess the dumpfile based on structure, or use type if provided
    # extract nodes by IP
    #
    # NOTES: we need to find where is this dump taken from
    # e.g. what is the 'center' or the current host (IP)
    # This will be useful when adding nodes to a graph, since two subnets might be adjacent
    # and have the same network address but be divided by a router with a different IP
    # ..or something like that.
    #
    # At the moment the imported_data structure could be a dictionary
    # { 'current_ip': [
    #       list of nodes, ...
    #   ]
    # }
    # return imported_data
    pass


def grow_graph(graph, imported_data):
    """Given a bunch of nodes, if they are not dupes add to graph"""
    # TODO
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
    imported_data = load_dump(args.dumpfile, args.dumpfile_type)
    grow_graph(graph, imported_data)
    save_graph(graph, savefile, args.force)

    exit(0)


if __name__ == '__main__':
    main()
