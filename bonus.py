#!/usr/bin/python

from constants import *

# Locations of bonus squares

bonuses = {
(0, 0): "TW", \
(0, 7): "TW", \
(0, 14): "TW", \
(7, 0): "TW", \
(7, 14): "TW", \
(14, 0): "TW", \
(14, 7): "TW", \
(14, 14): "TW", \
(0, 3): "TL", \
(0, 11): "TL", \
(2, 6): "TL", \
(2, 8): "TL", \
(3, 0): "TL", \
(3, 7): "TL", \
(3, 14): "TL", \
(6, 2): "TL", \
(6, 6): "TL", \
(6, 8): "TL", \
(6, 12): "TL", \
(7, 3): "TL", \
(7, 11): "TL", \
(8, 2): "TL", \
(8, 6): "TL", \
(8, 8): "TL", \
(8, 12): "TL", \
(11, 0): "TL", \
(11, 7): "TL", \
(11, 14): "TL", \
(12, 6): "TL", \
(12, 8): "TL", \
(14, 3): "TL", \
(14, 11): "TL", \
(1, 1): "DW", \
(1, 13): "DW", \
(2, 2): "DW", \
(2, 12): "DW", \
(3, 3): "DW", \
(3, 11): "DW", \
(4, 4): "DW", \
(4, 10): "DW", \
(7, 7): "DW", \
(10, 4): "DW", \
(10, 10): "DW", \
(11, 3): "DW", \
(11, 11): "DW", \
(12, 2): "DW", \
(12, 12): "DW", \
(13, 1): "DW", \
(13, 13): "DW", \
(1, 5): "DL", \
(1, 9): "DL", \
(5, 1): "DL", \
(5, 5): "DL", \
(5, 9): "DL", \
(5, 13): "DL", \
(9, 1): "DL", \
(9, 5): "DL", \
(9, 9): "DL", \
(9, 13): "DL", \
(13, 5): "DL", \
(13, 9): "DL" }

# Normal squares
for x in range(BOARDSIZE_X):
    for y in range(BOARDSIZE_Y):
        if (x, y) not in bonuses.keys():
            bonuses[(x, y)] = "N"

# Bonus square colors
colors = { "N": BKGROUND, "DL": DL, "TL": TL, "DW": DW, "TW": TW }
