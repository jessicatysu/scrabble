#!/usr/bin/python

from optparse import OptionParser
import Game
from constants import *

# Options processing
parser = OptionParser()
parser.add_option("-c", "--challenge", action="store_true", dest="challenge",
       default=False, help="Enable challenges (disabled by default)")
parser.add_option("-i", "--intl", action="store_true", dest="intl",
        default=False, help="Enable international dictionary")
(opts, args) = parser.parse_args()

# Create a game
game = Game.Game(opts.intl, opts.challenge)

game.startGame()
