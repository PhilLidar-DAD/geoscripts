#!/usr/bin/python2.7

import argparse
import gsquery
import logging
import os
import sys

_version = "0.2.1"
print os.path.basename(__file__) + ": v" + _version
_logger = logging.getLogger()
_LOG_LEVEL = logging.DEBUG
_CONS_LOG_LEVEL = logging.INFO


def _setup_logging(args):
    # Setup logging
    _logger.setLevel(_LOG_LEVEL)
    formatter = logging.Formatter("[%(asctime)s] %(filename)s \
(%(levelname)s,%(lineno)d) : %(message)s")

    # Check verbosity for console
    if args.verbose and args.verbose >= 1:
        global _CONS_LOG_LEVEL
        _CONS_LOG_LEVEL = logging.DEBUG

    # Setup console logging
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(_CONS_LOG_LEVEL)
    ch.setFormatter(formatter)
    _logger.addHandler(ch)


def _parse_arguments():
    # Parse arguments
    parser = argparse.ArgumentParser(epilog="Example: ./update_grid.py \
-fid DSM -gid E370N1851")
    parser.add_argument("--version", action="version",
                        version=_version)
    parser.add_argument("-v", "--verbose", action="count")
    parser.add_argument("-gid", "--grid-id", required=True,
                        help="GRIDREF")
    parser.add_argument("-fid", "--field-id", required=True,
                        help="DSM/DTM/ORTHO")
    parser.add_argument("-off", action="store_true",
                        help="Reset availability to 0")
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    # Parse arguments
    args = _parse_arguments()

    # Setup logging
    _setup_logging(args)

    success = gsquery.transacton_update("geonode:grid", "GRIDREF", args.grid_id,
                                        args.field_id, "0" if args.off else "1")
    if not success:
        _logger.info("Update failed:")
        _logger.error(success)
    else:
        _logger.info("Update successful!")
