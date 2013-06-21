#!/usr/bin/python

# This class represents the game display.

import curses
import random
from constants import *

class Display:
    def __init__(self, game):
        # Create the screen
        self.stdscr = curses.initscr()
        curses.noecho(); curses.cbreak; self.stdscr.keypad(1)
        self.stdscr.resize(SCRSIZE_Y, SCRSIZE_X)
        curses.start_color()

        # Initialize color pairs
        curses.init_pair(BKGROUND, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # Double letter squares
        curses.init_pair(DL, curses.COLOR_GREEN, curses.COLOR_CYAN)
        # Triple letter squares
        curses.init_pair(TL, curses.COLOR_GREEN, curses.COLOR_BLUE)
        # Double word squares
        curses.init_pair(DW, curses.COLOR_GREEN, curses.COLOR_RED)
        # Triple word squares
        curses.init_pair(TW, curses.COLOR_GREEN, curses.COLOR_MAGENTA)
        # Special debug color
        curses.init_pair(DEBUG, curses.COLOR_BLACK, curses.COLOR_WHITE)

        # Draw the screen
        self.drawScreen(game)
    
    # Check to see if coordinates are on screen
    def onScreen(self, x, y):
        if x in range(SCRSIZE_X) and y in range(SCRSIZE_Y):
            return True
        else:
            return False
    
    # Get one character of input
    def getch(self):
        return self.stdscr.getch()

    # Delete messages from screen
    def clearMsg(self, numLines = SCRSIZE_Y - MSG_Y - 1):
        for l in range(numLines): # number of lines to clear
            for i in range(SCRSIZE_X - MSG_X):
                self.stdscr.addch(MSG_Y + l, MSG_X + i, " ")
    
    # Print messages to screen
    def printMsg(self, msg, vertOffset = 0):
        assert vertOffset < SCRSIZE_Y - MSG_Y - 1, "Error message off screen"
        self.stdscr.addstr(MSG_Y + vertOffset, MSG_X, msg)
        
    def redrawRack(self, player):
        if player is None:
            return
        for i in range(7):
            self.stdscr.addch(RACK_Y, RACK_X + i, " ")
        for i in range(len(player.rack)):
            self.stdscr.addch(RACK_Y, RACK_X + i, player.rack[i])
        assert RACK_X >= 11, "Rack too far to left"
        self.stdscr.addstr(RACK_Y, RACK_X - 11, "Your rack: ")

    def shuffleRack(self, player):
        random.shuffle(player.rack)
        self.redrawRack(player)

    def moveCursor(self, x, y):
        self.stdscr.move(y, x)

    def drawScreen(self, game):
        self.drawBoard(game.board)
        self.drawButtons(game)
        self.drawStatus(game)
        self.drawBars()
        self.redrawRack(game.curPlayer)
    
    def redrawSquare(self, x, y, board, color=None):
        stdscr = self.stdscr
        square = board.squares[(x, y)]
        if color is None:
            color = square.color
        # Mark ordinary empty tiles with a dot
        if square.letter is None and square.bonus == "N":
            stdscr.addch(y, x, ".", curses.color_pair(color))
        # Leave bonus empty tiles blank
        elif square.letter is None and square.bonus != "N":
            stdscr.addch(y, x, " ", curses.color_pair(color))
        # Otherwise, mark them with their letter
        else:
            stdscr.addch(y, x, square.letter, curses.color_pair(color))
        
    # Draw the actual Scrabble board
    def drawBoard(self, board):
        for x in range(BOARDSTART_X, BOARDSTART_X + BOARDSIZE_X):
            for y in range(BOARDSTART_Y, BOARDSTART_Y + BOARDSIZE_Y):
                self.redrawSquare(x, y, board)
    
    # Draw buttons
    def drawButtons(self, game):
        for button in game.buttons:
            self.stdscr.addstr(button.ystart, button.xstart, button.name, \
                    curses.A_STANDOUT)

    # Print score and whose turn it is
    def drawStatus(self, game):
        # Clear score
        self.stdscr.addstr(SCORE_Y, SCORE_X, " " * (SCRSIZE_X - SCORE_X))
        self.stdscr.addstr(SCORE_Y + 1, SCORE_X, " " * (SCRSIZE_X - SCORE_X))
        # Draw score
        for i in range(len(game.players)):
            self.stdscr.addstr(SCORE_Y, SCORE_X + SCORE_SPC*i,
                    game.roster[i].name)
            self.stdscr.addstr(SCORE_Y + 1, SCORE_X + SCORE_SPC*i,
                    str(game.roster[i].score))
        # Draw turn
        if game.curPlayer is not None:
            self.stdscr.addstr(TURN_Y, TURN_X, " " * (SCRSIZE_X - TURN_X))
            self.stdscr.addstr(TURN_Y, TURN_X, game.curPlayer.name + "'s turn")
    
    # Draw bars on screen
    def drawBars(self):
        for x in range(BAR_H_LENGTH):
            self.stdscr.addch(BAR_HORIZ, x, " ", curses.A_STANDOUT)
        for y in range(BAR_V_LENGTH):
            self.stdscr.addch(BAR_VERT, y, " ", curses.A_STANDOUT)

    # Closes the display
    def close(self):
        curses.nocbreak(); self.stdscr.keypad(0); curses.echo()
        curses.endwin()
    
    # Paints the given square a special color.
    def debugColor(self, x, y, board):
        self.redrawSquare(x, y, board, DEBUG)
