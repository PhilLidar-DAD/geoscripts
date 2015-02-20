#!/usr/bin/python2.7

import argparse
import gdaltools
import gsquery
import itertools
import json
import logging
import os
import pprint
import sys

_version = "0.04.16"
print os.path.basename(__file__) + ": v" + _version
_logger = logging.getLogger()
_LOG_LEVEL = logging.DEBUG
_CONS_LOG_LEVEL = logging.INFO
_COLLATION_SETTINGS_JSON = "collation_settings.json"


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version",
                        version=_version)
    parser.add_argument("-v", "--verbose", action="count")
    args = parser.parse_args()
    return args


def _get_rb_assignment(typeName):
    for river_basin, prefixes in collation_settings.items():
        for prefix in prefixes:
            if ":".join(typeName).startswith(prefix):
                return river_basin


def _startswith(layer_name, coverage_type, collation_key):
    for match_key in collation_settings["collation_keys"][collation_key]:
        if layer_name.startswith(coverage_type + "_" + match_key):
            return True
    return False

# Parse arguments
_logger.info("Parsing arguments...")
args = _parse_arguments()

# Silence requests library log
logging.getLogger("requests").setLevel(logging.WARNING)

# Setup logging
_setup_logging(args)

# Load collation settings assignment
collation_settings = json.load(open(_COLLATION_SETTINGS_JSON, "r"))
_logger.info("Collation settings:\n%s", pprint.pformat(collation_settings))

# Get features list
features = gsquery.get_features_list()
_logger.info("Features list:\n%s", pprint.pformat(features))

# For each coverage type
total_areas = {}
unmatched_layers = []

# Collate features
_logger.info("Collating features...")
while features:
    # Get a feature
    feature = features.pop()
    _logger.debug("feature = %s", feature)

    has_match = False
    for coverage_type, collation_key in \
        itertools.product(sorted(collation_settings["coverage_types"]),
                          sorted(collation_settings["collation_keys"])):

        # Initialize dictionaries
        if not collation_key in total_areas:
            total_areas[collation_key] = {}
        if not coverage_type in total_areas[collation_key]:
            total_areas[collation_key][coverage_type] = {"area": 0.,
                                                         "features": []}

        # Extract workspace and layer names
        workspace, layer_name = feature

        # Check if layer name matches
        if (workspace == collation_settings["workspace"] and
                _startswith(layer_name, coverage_type, collation_key)):

            # Add feature to list
            total_areas[collation_key][coverage_type][
                "features"].append(feature)
            has_match = True

    if not has_match:
        unmatched_layers.append(feature)

_logger.debug("total_areas =\n%s", pprint.pformat(total_areas))
_logger.info("Unmatched layers:\n%s", pprint.pformat(unmatched_layers))

# Get/compute areas
_logger.info("Getting/computing areas...")
for collation_key, collation_value in total_areas.viewitems():

    _logger.info("Collation key: %s", collation_key)

    for coverage_type, coverage_info in collation_value.viewitems():

        if len(coverage_info["features"]) >= 2:

            # Union then compute area

            # Get geometries
            _logger.info("Getting geometries...")
            geoms = []

            for typeName in coverage_info["features"]:

                # Get geometry of feature
                geom = gsquery.get_feature_property(typeName, "the_geom")

                # Add geom to list
                geoms.append(geom)

            # Get union of geometries
            _logger.info("Computing union...")
            union = gdaltools.union(geoms)

            # Get area of union
            _logger.info("Computing area of union...")
            area = gdaltools.area(union)

            coverage_info["area"] = area
            _logger.debug("area = %s", area)

        elif len(coverage_info["features"]) >= 1:

            typeName = coverage_info["features"][0]

            # Get area of the only feature
            _logger.info("Getting area of %s...", ":".join(typeName))
            area = gsquery.get_feature_property(typeName, "Area")

            if area is None:
                _logger.info("No Area field found. Computing area...")

                # Get geometry of feature
                _logger.info("Getting geometry of %s...", ":".join(typeName))
                geom = gsquery.get_feature_property(typeName, "the_geom")

                area = gdaltools.area(geom)

            coverage_info["area"] = area
            _logger.debug("area = %s", area)

_logger.debug("total_areas =\n%s", pprint.pformat(total_areas))

# Generate CSV report
with open("report_areas.csv", "w") as report_file:
    # Write column headers
    report_file.write(",".join(["river basins"] +
                               sorted(collation_settings["coverage_types"])))
    report_file.write("\n")
    # Write collation key data per row
    for collation_key, collation_value in sorted(total_areas.viewitems()):
        row = [collation_key] + ["%.2f" % coverage_info["area"]
                                 for _, coverage_info
                                 in sorted(collation_value.viewitems())]
        report_file.write(",".join(row))
        report_file.write("\n")
    report_file.write(2 * "\n")
    # Write unmatched layers
    report_file.write("Unmatched layers:\n")
    report_file.write("\n".join(":".join([i, j]) for i, j in unmatched_layers))
