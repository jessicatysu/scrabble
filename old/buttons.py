#!/usr/bin/python

# This file contains methods to determine whether coordinates are on various
# board elements.

from constants import *

# Check to see if coordinates are on SHUFFLE button.
def onShuffleButton(x, y):
   if x in range(SHUFFLE_X, SHUFFLE_X + 7) and y == SHUFFLE_Y:
      return True
   else:
      return False

# Are coordinates on RECALL button?
def onRecallButton(x, y):
   if x in range(RECALL_X, RECALL_X + 6) and y == RECALL_Y:
      return True
   else:
      return False

# Are coordinates on PASS/EXCHANGE button?
def onPassButton(x, y):
   if x in range(PASS_X, PASS_X + 13) and y == PASS_Y:
      return True
   else:
      return False

# Are coordinates on UNDO button?
def onUndoButton(x, y):
   if x in range(UNDO_X, UNDO_X + 4) and y == UNDO_Y:
      return True
   else:
      return False

# What about the CHALLENGE button?
def onChallengeButton(x, y):
   if x in range(CHALLENGE_X, CHALLENGE_X + 9) and y == CHALLENGE_Y:
      return True
   else:
      return False

# Or the QUIT button?
def onQuitButton(x, y):
   if x in range(QUIT_X, QUIT_X + 4) and y == QUIT_Y:
      return True
   else:
      return False

# Are the coordinates on the screen?
def onScreen(x, y):
   if x in range(SCRSIZE_X) and y in range(SCRSIZE_Y):
      return True
   else:
      return False

# What about on the board?
def onBoard(x, y):
   if x in range(BOARDSTART_X, BOARDSTART_X + BOARDSIZE_X) and \
      y in range(BOARDSTART_Y, BOARDSTART_Y + BOARDSIZE_Y):
      return True
   else:
      return False
