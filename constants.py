#!/usr/bin/python

# This file contains constants such as the ASCII representation of keypresses
# and the locations of various elements on the board.

# Some constants that have to do with placement of board elements
RACK_X = 15 # x and y coordinates of the start of the rack string
RACK_Y = 19
SCORE_X = 18 # x and y coordinates of the start of the first player's score
SCORE_Y = 1
TURN_X = 3 # x and y coordinates of the start of the thing that says "X's turn"
TURN_Y = 17
MSG_X = 34 # coordinates of error message location
MSG_Y = 19
#UNDO_X = 20 # position of undo button (not currently implemented)
#UNDO_Y = 5
SUBMIT_X = 20
SUBMIT_Y = 5
CHALLENGE_X = 20 # position of challenge button
CHALLENGE_Y = 7
QUIT_X = 20 # position of quit button
QUIT_Y = 9
SHUFFLE_X = 2
SHUFFLE_Y = 21
RECALL_X = 11
RECALL_Y = 21
PASS_X = 19
PASS_Y = 21
SCRSIZE_X = 80
SCRSIZE_Y = 24
BOARDSIZE_X = 15 # size of scrabble board
BOARDSIZE_Y = 15
BOARDSTART_X = 0 # location of scrabble board
BOARDSTART_Y = 0
CENTER_X = 7 # Position of center square
CENTER_Y = 7
SCORE_SPC = 9 # Space between two players' scores
BAR_HORIZ = 16 # Position of standout bars
BAR_VERT = 16
BAR_H_LENGTH = SCRSIZE_X
BAR_V_LENGTH = 16

# Numerical representation of keypresses
KEY_NEWLINE = 10
KEY_SPACE = 32
KEY_S = 115
KEY_H = 104
KEY_J = 106
KEY_K = 107
KEY_L = 108
KEY_Y = 121
KEY_U = 117
KEY_B = 98
KEY_N = 110
KEY_Q = 113
KEY_BACKSPACE = 8
KEY_DEL = 127
KEY_ESC = 27

# Color pairs
BKGROUND = 1 # black background
DL = 2 # cyan background
TL = 3 # blue background
DW = 4 # red background
TW = 5 # magenta background
DEBUG = 6

# Other constants
BINGO_BONUS = 50
