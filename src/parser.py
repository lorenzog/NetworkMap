#!/usr/bin/env python2.7
"""
POC of python parser
====================

By default it adds to a local sqlite instance.

.. note:
    What's the best way to store a data structure like this one on disk?

"""
import argparse
import logging
import os
# TODO SQLite


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def main():
    p = argparse.ArgumentParser("Network mapper")
    # TODO if dumpfile is not specified, assume we're doing db maintenance like 'export to db'?
    p.add_argument('dumpfile')
    p.add_argument('-t', '--dumpfile-type')
    p.add_argument('--clear', help="Clears the database")
    p.add_argument('-d', '--debug', action='store_true')
    args = p.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    if args.dumpfile_type is None:
        # TODO
        # try to guess/determine file type?
        pass

    if not os.path.exists(args.dumpfile):
        raise SystemError("File {} does not exist".format(args.dumpfile))

    exit(0)


if __name__ == '__main__':
    main()
