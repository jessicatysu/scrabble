#!/usr/bin/python


# This class contains the internal logic of the game (scoring, checking
# validity of plays, etc.)

import re
from constants import *
from letters import *

class Play:
    def __init__(self, game, player):
        self.player = player
        # List of squares in play
        self.squares = player.used
        # List of words (each word is a string)
        self.words = self.getWords(game)
        self.score = self.scorePlay(game)
    
    # Check to see if the play is a legal Scrabble move
    def isLegal(self, game):
        if len(self.squares) == 0: # Null plays illegal
            return False
        if len(game.plays) == 0 and not self.passThroughCenter():
            return False # First move passes through center
        if len(game.plays) == 0 and len(self.squares) == 1:
            return False # No one-tile plays on the first move
        if self.squaresFormWord(game.board) and \
                (self.connectedToBoard(game) or len(game.plays) == 0):
            return True # All subsequent moves should be connected to the board
        return False
    
    # Check to see if a challenge should take the play off the board
    def isValid(self, game):
        if not self.isLegal(game):
            return False
        for word in self.words:
            if verifyWord(word, game) == False:
                return False
        return True
    
    # This returns a score.
    def scorePlay(self, game):
        try:
            wordList = self.findWordSquares(game)
        except BadPlayError:
            return 0
        playScore = 0
        for wordSquares in wordList:
            wordScore = 0
            wordBonus = 1
            # Add the values of each letter (including letter bonuses)
            for square in wordSquares:
                if square.bonus == "N" or square not in self.squares:
                    # No bonus if tile is old or it is not a bonus square
                    letterScore = score[square.letter] 
                elif square.bonus == "DL":
                    letterScore = score[square.letter] * 2
                elif square.bonus == "TL":
                    letterScore = score[square.letter] * 3
                elif square.bonus == "DW":
                    letterScore = score[square.letter]
                    wordBonus *= 2
                elif square.bonus == "TW":
                    letterScore = score[square.letter]
                    wordBonus *= 3
                else:
                    assert False, "Wrong bonus value: " + square.bonus
                wordScore += letterScore
            wordScore *= wordBonus
            playScore += wordScore
        
        if len(self.squares) == 7:
            playScore += BINGO_BONUS
        return playScore

    ######### Internal methods ##########
    
    # Check to see if the squares have the same horizontal component
    def squaresInHorizLine(self):
        assert len(self.squares) > 0, "Must have at least one square"
        for square in self.squares:
            if square.y != self.squares[0].y:
                return False
        return True
    
    # Check to see if the squares have the same vertical component
    def squaresInVertLine(self):
        assert len(self.squares) > 0, "Must have at least one square"
        for square in self.squares:
            if square.x != self.squares[0].x:
                return False
        return True
    
    # Check to see if squares form one word
    def squaresFormWord(self, board):
        assert len(self.squares) > 0, "Must have at least one square"
        if not self.squaresInHorizLine() and not self.squaresInVertLine():
            return False
        # Check that there exists a path of occupied squares between the 
        # first square and all other squares
        for square in self.squares:
            if not existsPath(square, self.squares[0], board):
                return False
        return True
    
## old code from squaresFormWord        
#        if len(self.squares) == 1:
#            return True
#        # Get list of x coordinates (if play is vertical) or y coordinates
#        # (if play is horizontal), then sort the list and check to see
#        # that it is a list of consecutive integers.
#        coords = []
#        if self.squaresInHorizLine():
#            for square in self.squares:
#                coords.append(square.x)
#        elif self.squaresInVertLine():
#            for square in self.squares:
#                coords.append(square.y)
#        else:
#            return False
#        
#        coords.sort()
#        for i in range(1, len(coords)):
#            if coords[i] != coords[i-1] + 1:
#                return False
#        return True
        
    # Check to see if squares are adjacent to any other square on the board
    def connectedToBoard(self, game):
        assert len(self.squares) > 0, "Must have at least one square"
        # Get a set of all occupied squares on the board
        occupiedSquares = set()
        for coords in game.board.squares.keys():
            if game.board.squares[coords].letter != None:
                occupiedSquares.add(game.board.squares[coords])
        
        # Get a list of all occupied squares on the board that aren't
        # being used in the current play
        oldSquares = list(occupiedSquares.difference(set(self.squares)))

        # Check if squares are connected to old squares
        for square in self.squares:
            if square.connectedTo(oldSquares):
                return True
        return False

    # Check to see if squares pass through center
    def passThroughCenter(self):
        for square in self.squares:
            if square.x == CENTER_X and square.y == CENTER_Y:
                return True
        return False

    # This returns a list of "words," where each word is a list of squares
    # that make up that word.
    def findWordSquares(self, game):
        if not self.isLegal(game):
            raise BadPlayError()
        wordList = []
        if self.squaresInHorizLine():
            for square in self.squares:
                wordList.append(self.vertSeek(game, square))
            wordList.append(self.horizSeek(game, self.squares[0]))
        elif self.squaresInVertLine():
            for square in self.squares:
                wordList.append(self.horizSeek(game, square))
            wordList.append(self.vertSeek(game, self.squares[0]))
        else:
            assert False, "Squares not in a line"
        # Return the list, pruned of None's
        return [word for word in wordList if word is not None]
    
    # This tries to find a word containing a given square in the vertical
    # direction.
    def vertSeek(self, game, square):
        squares = game.board.squares
        word = [square]
        x = square.x
        y = square.y
        while game.board.onBoard(x, y-1) and squares[(x, y-1)].letter != None:
            if squares[(x, y-1)] not in word:
                word.append(squares[(x, y-1)])
            y -= 1
        while game.board.onBoard(x, y+1) and squares[(x, y+1)].letter != None:
            if squares[(x, y+1)] not in word:
                word.append(squares[(x, y+1)])
            y += 1
        if len(word) > 1:
            return self.sortWordSquares(word)
        else:
            return None

    # This tries to find a word containing a given square in the horizontal
    # direction.
    def horizSeek(self, game, square):
        squares = game.board.squares
        word = [square]
        x = square.x
        y = square.y
        while game.board.onBoard(x-1, y) and squares[(x-1, y)].letter != None:
            if squares[(x-1, y)] not in word:
                word.append(squares[(x-1, y)])
            x -= 1
        while game.board.onBoard(x+1, y) and squares[(x+1, y)].letter != None:
            if squares[(x+1, y)] not in word:
                word.append(squares[(x+1, y)])
            x += 1
        if len(word) > 1:
            return self.sortWordSquares(word)
        else:
            return None

    # This sorts a list of squares.
    def sortWordSquares(self, squares):
        # Sort by x coordinate (does nothing for vertical words)
        squares.sort(compareX)
        # Sort by y coordinate (does nothing for horizontal words)
        squares.sort(compareY)
        return squares
    
    # This returns a string from a list of squares.
    def getWord(self, squares):
        wordSquares = self.sortWordSquares(squares)
        string = ""
        for square in wordSquares:
            string += square.letter
        return string
    
    # This returns a list of strings of words used in the play.
    def getWords(self, game):
        try:
            wordList = self.findWordSquares(game)
        except BadPlayError:
            return None
        words = []
        for wordSquares in wordList:
            words.append(self.getWord(wordSquares))
        return words

# Bad play exception
class BadPlayError(Exception):
    pass

# Checks to see if a word is in the dictionary
def verifyWord(word, game):
    dict = open(game.dictionary, 'r')
    for line in dict:
        if word == line.rstrip():
            dict.close()
            return True
    dict.close()
    return False

# Compares two squares by x coordinate
def compareX(sq1, sq2):
    return sq1.x - sq2.x

# Compares two squares by y coordinate
def compareY(sq1, sq2):
    return sq1.y - sq2.y

# Check if there exists a path between two squares such that each tile
# on the path is occupied
def existsPath(sq1, sq2, board):
    for x in range(min(sq1.x, sq2.x), max(sq1.x, sq2.x) + 1):
        for y in range(min(sq1.y, sq2.y), max(sq1.y, sq2.y) + 1):
            if board.squares[(x, y)].letter is None:
                return False
    return True

