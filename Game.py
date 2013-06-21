#!/usr/bin/python

import random
import sys
from collections import deque
import letters
import Player
import Play
import Button
import Display
from bonus import *

#### These classes represent the game and board.

# This class represents a Scrabble game.
class Game:
    def __init__(self, intl, challenge):
        self.players = deque() # Rotating queue of players
        self.roster = [] # Static list of players (used for screen display)
        self.curPlayer = None
        self.plays = []
        self.gameOver = False
        self.challenge = challenge
        self.board = Board() # Create board

        # Choose dictionary
        if intl is True:
            self.dictionary = "sowpods.txt"
        else:
            self.dictionary = "TWL06.txt"

        # Add players to game
        self.addPlayers()
        
        # Buttons on board
        self.passButton = Button.PassButton()
        self.recallButton = Button.RecallButton()
        self.quitButton = Button.QuitButton()
        self.challengeButton = Button.ChallengeButton(self.challenge)
        self.shuffleButton = Button.ShuffleButton()
        self.submitButton = Button.SubmitButton()
        self.buttons = [self.passButton, self.recallButton, self.quitButton, \
                self.challengeButton, self.shuffleButton, self.submitButton]

        self.display = Display.Display(self) # Create display

        # Fill bag with tiles
        self.bag = []
        for letter in letters.frequency.keys():
            # letters.frequency[letter] is the number of tiles
            # there should be in the bag of a certain type.
            for i in range(letters.frequency[letter]):
                self.bag.append(letter)
    
    def startGame(self):
        random.seed() # For choosing tiles randomly, and shuffling
        # Draw the display
        self.display.drawScreen(self)
        
        # Enter game loop
        while self.gameOver == False:
            # Choose a player to play
            player = self.players.popleft()
            self.players.append(player)
            self.curPlayer = player

            # Ask the player to take his turn
            player.takeTurn(self)
        
        # End of game
        self.display.close()
        print "\nGame Over"
        for player in self.roster:
            print player.name, "scored", player.score, "points"
        print "Everyone did fantastic!\n"
    
    # Add players to game
    def addPlayers(self):
        print "\nWelcome to terminal Scrabble!  Using dictionary " + self.dictionary
        try:
            numPlayers = int(raw_input("Please enter the number of players. "))
            if numPlayers < 2 or numPlayers > 4:
                sys.exit("Scrabble is a game for 2-4 people\n")
        except:
            sys.exit("Must enter a number between 2 and 4\n")
        for i in range(numPlayers):
            name = raw_input("Enter name of player " + str(i+1) + ": ")
            # Names cannot be too short or too long
            if len(name) < 1 or len(name) > 8:
                name = "Player " + str(i+1)
            self.players.append(Player.Player(self, name))
        self.roster = list(self.players)

    def endGame(self):
        self.gameOver = True
    
    # Go backwards in the turn order (allows person to take another turn
    # if called once; goes to the previous person if called twice)
    def repeatTurn(self):
        self.players.appendleft(self.players.pop())
        self.curPlayer.newTurn = False
    
    # Exits, writing a debug message to the screen
    def writeErr(self, error):
        self.display.close()
        sys.exit("Debug: " + error)

# This class represents a Scrabble board.
class Board:
    def __init__(self):
        # Add squares to the board
        self.squares = {}
        for x in range(BOARDSIZE_X):
            for y in range(BOARDSIZE_Y):
                letter = None
                self.squares[(x, y)] = Square(x, y, letter)

    def changeLetter(self, x, y, letter):
        square = self.squares[(x, y)]
        square.letter = letter
        if letter is None:
            square.color = colors[bonuses[(x, y)]]
        else:
            square.color = BKGROUND
    
    def onBoard(self, x, y):
        if x in range(BOARDSTART_X, BOARDSTART_X + BOARDSIZE_X):
            if y in range(BOARDSTART_Y, BOARDSTART_Y + BOARDSIZE_Y):
                return True
        return False

class Square:
    def __init__(self, x, y, letter):
        self.bonus = bonuses[(x, y)] # "DL", "DW", "TL", "TW", "N"
        self.color = colors[self.bonus]
        self.letter = letter
        self.x = x
        self.y = y
    
    def isOccupied(self):
        if self.letter is not None:
            return True
        else:
            return False
    
    # Checks to see if the square is connected to any square in a list of
    # other squares.
    def connectedTo(self, squares):
#        assert onBoard(self.x, self.y), "Square not on board!"
        for square in squares:
            if (abs(square.x - self.x) == 1 and square.y == self.y) \
                    or (abs(square.y - self.y) == 1 and square.x == self.x):
                return True
        return False
