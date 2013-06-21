#!/usr/bin/python

from constants import *
import re
import random
import Display
import Play

class Button:
    def __init__(self, name, xstart, ystart, length):
        self.name = name
        self.xstart = xstart
        self.ystart = ystart
        self.length = length

    # Checks if the given coordinates are on the button.
    def onButton(self, x, y):
        if x in range(self.xstart, self.xstart + self.length) and y == self.ystart:
            return True
        else:
            return False

# Behavior for different buttons on the screen
class PassButton(Button):
    def __init__(self):
        self.name = "PASS/EXCHANGE"
        self.xstart = PASS_X
        self.ystart = PASS_Y
        self.length = 13
    
    # Code for exchanging tiles
    def click(self, game, player):
        # First, return all tiles to rack
        recall(game, player)

        # Display exchange messages
        game.display.clearMsg()
        if len(game.bag) < 7:
            game.display.printMsg("Cannot exchange with fewer than 7 tiles")
            game.display.printMsg("(press Enter to pass or Esc to cancel)", vertOffset = 1)
        else:
            game.display.printMsg("Exchange tiles: ")
            game.display.printMsg("(press Enter to change or Esc to cancel)", vertOffset = 1)
            
        
        # Enter exchange loop
        while 1:
            c = game.display.getch()
            if c == KEY_NEWLINE: # Exchange selected tiles
                self.exchange(game, player)
                break
            elif c == KEY_BACKSPACE or c == KEY_DEL: # Delete tile to be exchanged
                self.pop(game, player)
            elif c == KEY_ESC: # Cancel exchange of tiles
                while len(player.exchanged) > 0:
                    self.pop(game, player)
                game.repeatTurn() # Allow player to "take another turn"
                break
            elif c == KEY_Q: # Quit game
                game.endGame()
                break
            elif re.match("[A-Z]|\.", chr(c)): # Add tile to exchange rack
                if player.rack.count(chr(c)) > 0 and len(game.bag) >= 7:
                    self.push(game, player, c)
            else:
                pass
    
    # Exchange tiles currently on exchange rack
    def exchange(self, game, player):
        game.display.clearMsg()
        while len(player.rack) < 7:
            tile = random.choice(game.bag)
#            player.rack.append(tile)
            player.addToRack(game, tile)
            game.bag.remove(tile)
        for tile in player.exchanged:
            game.bag.append(tile)
        player.exchanged = []
#        game.display.redrawRack(player)
    
    # Remove one tile from exchange rack
    def pop(self, game, player):
#        player.rack.append(player.exchanged.pop())
        player.addToRack(game, player.exchanged.pop())
#        game.display.redrawRack(player)
        game.display.clearMsg(1)
        game.display.printMsg("Exchange tiles: " + "".join(player.exchanged))

    # Add one tile to exchange rack
    def push(self, game, player, c):
        player.exchanged.append(chr(c))
        player.removeFromRack(game, chr(c))
#        player.rack.remove(chr(c))
#        game.display.redrawRack(player)
        game.display.clearMsg(1)
        game.display.printMsg("Exchange tiles: " + "".join(player.exchanged))

class QuitButton(Button):
    def __init__(self):
        self.name = "QUIT"
        self.xstart = QUIT_X
        self.ystart = QUIT_Y
        self.length = 4
    
    def click(self, game, player):
        game.endGame()

class ChallengeButton(Button):
    def __init__(self, challenge):
        self.name = "CHALLENGE"
        self.xstart = CHALLENGE_X
        self.ystart = CHALLENGE_Y
        self.length = 9
        self.challenge = challenge
    
    # Code for challenges
    def click(self, game, player):
        recall(game, player)
        
        if self.challenge is False:
            game.display.clearMsg()
            game.display.printMsg("Challenges disabled")
            game.repeatTurn()
            return
        if len(game.plays) == 0:
            game.display.clearMsg()
            game.display.printMsg("No plays to challenge")
            game.repeatTurn()
            return
        if player.canChallenge is False:
            game.display.clearMsg()
            game.display.printMsg("Cannot make any more challenges this turn")
            game.repeatTurn()
            return

        player.canChallenge = False # Do not allow player to challenge twice
        
        assert len(game.plays) > 0, "No plays in stack"
        lastPlay = game.plays.pop()
        if lastPlay.isValid(game): # Challenge unsuccessful
            game.plays.append(lastPlay)
        else:
            # Reduce score
            lastPlay.player.score -= lastPlay.score
            # Remove tiles from board, returning them to player's rack
            for square in lastPlay.squares:
                lastPlay.player.rack.append(square.letter)
                game.board.changeLetter(square.x, square.y, None)
                game.display.redrawSquare(square.x, square.y, game.board)
            game.repeatTurn() # Allow player to "take another turn"

# Recalls tiles to rack
class RecallButton(Button):
    def __init__(self):
        self.name = "RECALL"
        self.xstart = RECALL_X
        self.ystart = RECALL_Y
        self.length = 6

    def click(self, game, player):
        recall(game, player)
        game.repeatTurn()

# Undo button - not currently implemented
#class UndoButton(Button):
#    def __init__(self):
#        self.name = "UNDO"
#        self.xstart = UNDO_X
#        self.ystart = UNDO_Y
#        self.length = 4
#
#    def click(self, game, player):
#        pass

class ShuffleButton(Button):
    def __init__(self):
        self.name = "SHUFFLE"
        self.xstart = SHUFFLE_X
        self.ystart = SHUFFLE_Y
        self.length = 7

    def click(self, game, player):
        game.display.shuffleRack(player)
        game.repeatTurn() # Take another turn

class SubmitButton(Button):
    def __init__(self):
        self.name = "SUBMIT"
        self.xstart = SUBMIT_X
        self.ystart = SUBMIT_Y
        self.length = 6
    
    def click(self, game, player):
        if player.used == []: # Null play
            game.repeatTurn()
            return
        play = Play.Play(game, player)
        # Invalid plays
        if not play.isLegal(game) or (not game.challenge and not play.isValid(game)):
            game.display.clearMsg()
            game.display.printMsg("Illegal move")
            recall(game, player)
            game.repeatTurn()
        else:
            game.display.clearMsg()
            game.display.printMsg(player.name + " scored " + \
                    str(play.score) + " points!")
            game.plays.append(play)
            player.score += play.score
            player.newTurn = True
        player.used = []

# Brings tiles back to rack
def recall(game, player):
    for square in player.used:
        player.addToRack(game, square.letter)
#        player.rack.append(square.letter)
        game.board.changeLetter(square.x, square.y, None)
        game.display.redrawSquare(square.x, square.y, game.board)
#        game.display.redrawRack(player)
    player.used = []
