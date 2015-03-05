#!/usr/bin/python

import math

# Tile size in meters
_TILE_SIZE = 1000

def _floor(x):
    return int(math.floor(x / float(_TILE_SIZE)) * _TILE_SIZE)


def _ceil(x):
    return int(math.ceil(x / float(_TILE_SIZE)) * _TILE_SIZE)

if __name__ == '__main__':

    # Given the Eastings (x) and Northings (y) coordinates in the same projection
    # as the source
    x = 123456.789
    y = 234567.891
    print "Some coordinate: ({0}, {1})".format(x, y)

    # The coordinates of the upper left corner should be
    ul_x, ul_y = _floor(x), _ceil(y)
    # Upper right
    ur_x, ur_y = _ceil(x), _ceil(y)
    # Lower left
    ll_x, ll_y = _floor(x), _floor(y)
    # Lower right
    lr_x, lr_y = _ceil(x), _floor(y)

    print "Upper left: ({0}, {1})".format(ul_x, ul_y)
    print "Upper right: ({0}, {1})".format(ur_x, ur_y)
    print "Lower left: ({0}, {1})".format(ll_x, ll_y)
    print "Lower right: ({0}, {1})".format(lr_x, lr_y)