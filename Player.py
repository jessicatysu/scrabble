#!/usr/bin/python

import curses
import random
import Display
import sys
from constants import *

#### This class represents a Scrabble player.
class Player:
    def __init__(self, game, name):
        self.name = name
        self.score = 0
        self.rack = []
        self.used = [] # Squares a player is using this turn (not exchanging)
        self.exchanged = [] # Letters a player is exchanging this turn
        # This variable is true if it is the start of the player's turn (real
        # turn, not game "turn.")  Players take extra "turns" if they (for instance)
        # challenge other players.
        self.newTurn = True
        # True iff the player is allowed to challenge.  (as in, hasn't just
        # challenged someone)
        self.canChallenge = True
    
    def addToRack(self, game, letter):
        self.rack.append(letter)
        game.display.redrawRack(self)
    
    def removeFromRack(self, game, letter):
        self.rack.remove(letter)
        game.display.redrawRack(self)

    def addToUsed(self, game, square):
        self.used.append(square)
        game.display.clearMsg()
        game.display.printMsg("Letters used: " + \
                "".join([tile.letter for tile in self.used]))

    def removeFromUsed(self, game, square):
        self.used.remove(square)
        game.display.clearMsg()
        game.display.printMsg("Letters used: " + \
                "".join([tile.letter for tile in self.used]))

    def drawTiles(self, game):
        # Draw tiles from bag
        while len(self.rack) < 7 and len(game.bag) > 0:
            tile = random.choice(game.bag)
            self.addToRack(game, tile)
#            self.rack.append(tile)
            game.bag.remove(tile)
        game.display.redrawRack(self)
        

    def takeTurn(self, game):
        assert len(self.rack) <= 7, "Rack too long"

        if self.newTurn is True:
            self.drawTiles(game)
            self.canChallenge = True

        # Refresh display
        display = game.display
        display.drawStatus(game) # Score, whose turn it is
#        display.redrawRack(self)
#        display.clearMsg()

        while 1:
            # Get input
            scr = display.stdscr
            c = scr.getch()
            position = scr.getyx()
            x = position[1]
            y = position[0]
            
            # Submit command
            if c == KEY_NEWLINE:
                if game.board.onBoard(x, y):
                    game.submitButton.click(game, self)
                elif game.submitButton.onButton(x, y):
                    game.submitButton.click(game, self)
                elif game.passButton.onButton(x, y):
                    game.passButton.click(game, self)
                elif game.recallButton.onButton(x, y):
                    game.recallButton.click(game, self)
                elif game.challengeButton.onButton(x, y):
                    game.challengeButton.click(game, self)
                elif game.quitButton.onButton(x, y):
                    game.quitButton.click(game, self)
                elif game.shuffleButton.onButton(x, y):
                    game.shuffleButton.click(game, self)
                else:
                    continue
                break # Ends turn; some buttons let you take another turn
            
            # Movement keys
            elif c == curses.KEY_LEFT or c == KEY_H:
                if game.display.onScreen(x-1, y):
                    display.moveCursor(x-1, y)
            elif c == curses.KEY_RIGHT or c == KEY_L:
                if game.display.onScreen(x+1, y):
                    display.moveCursor(x+1, y)
            elif c == curses.KEY_UP or c == KEY_K:
                if game.display.onScreen(x, y-1):
                    display.moveCursor(x, y-1)
            elif c == curses.KEY_DOWN or c == KEY_J:
                if game.display.onScreen(x, y+1):
                    display.moveCursor(x, y+1)
            # yubn moves diagonally (nethack-style)
            elif c == KEY_Y:
                if game.display.onScreen(x-1, y-1):
                    display.moveCursor(x-1, y-1)
            elif c == KEY_U:
                if game.display.onScreen(x+1, y-1):
                    display.moveCursor(x+1, y-1)
            elif c == KEY_B:
                if game.display.onScreen(x-1, y+1):
                    display.moveCursor(x-1, y+1)
            elif c == KEY_N:
                if game.display.onScreen(x+1, y+1):
                    display.moveCursor(x+1, y+1)
            
            # Remove tile from board and place it onto rack
            elif c == KEY_BACKSPACE or c == KEY_DEL:
                # Choose the tile that the cursor is over
                square = None
                for s in self.used:
                    if s.x == x and s.y == y:
                        square = s
    
                if square is not None:
                    # Add tile to rack, removing it from board
                    self.removeFromUsed(game, square)
#                    self.used.remove(square)
                    self.addToRack(game, square.letter)
#                    self.rack.append(square.letter)
                    game.board.changeLetter(square.x, square.y, None)
                    # Update display
#                    display.redrawRack(self)
                    display.redrawSquare(square.x, square.y, game.board)
#                    display.clearMsg()
#                    display.printMsg("Letters used: " + \
#                        "".join([tile.letter for tile in self.used]))
                    display.moveCursor(square.x + 1, square.y)

            # Shuffle the rack
            elif c == KEY_SPACE or c == KEY_S:
                game.shuffleButton.click(game, self)
            
            # Quit the game
            elif c == KEY_Q and not game.board.onBoard(x, y):
                game.quitButton.click(game, self)
                break
            
            # Add tiles
            elif game.board.onBoard(x, y) and not game.board.squares[(x, y)].isOccupied():
                square = game.board.squares[(x, y)]
                if chr(c) in self.rack:
                    # Add tile to board
#                    self.rack.remove(chr(c))
                    game.board.changeLetter(square.x, square.y, chr(c))
                    self.addToUsed(game, square)
                    self.removeFromRack(game, chr(c))
#                    self.used.append(square)

                    # Update display
#                    display.redrawRack(self)
                    display.redrawSquare(square.x, square.y, game.board)
#                    display.clearMsg()
#                    display.printMsg("Letters used: " + \
#                        "".join([tile.letter for tile in self.used]))
                    display.moveCursor(square.x + 1, square.y)
            
            else:
                pass
