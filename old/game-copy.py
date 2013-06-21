#!/usr/bin/python

import curses
import letters # Letter scores and distributions
import bonus # Locations of bonus squares
import random
import re
from optparse import OptionParser
from constants import *
from buttons import * # Functions determining if coordinates are on board elements

# Command-line options
parser = OptionParser()
parser.add_option("-c", "--challenge", action="store_true", dest="challenge", 
                  default=False, help="Enable challenges (disabled by default)")
parser.add_option("-d", "--dictionary", dest="dict", default="twl",
                  help="Choose dictionary (pick \"twl\" or \"sowpods\")")
(options, args) = parser.parse_args()

# Choose your dictionary
if options.dict == "sowpods":
    dictionary = open('sowpods.txt', 'r') # SOWPODS dictionary - International
else:
    dictionary = open('TWL06.txt', 'r')     #TWL dictionary - American

# --------------------------------------------
# Defines a "player" class
class Player:
    def __init__(player, name):
        player.name = name
        player.score = 0
        player.rack = []
        player.index = -1

# Defines a class for a square on the board
class Square:
    def __init__(square, x, y, multiplier):
        square.x = x
        square.y = y
        # Note that the multiplier gets set to 1 when a tile is placed
        # on the board
        square.multiplier = multiplier
        square.letter = ""
        square.age = -1

# Defines a class for a tile that hasn't yet been placed on the board
class Tile:
    def __init__(tile, x, y, letter):
        tile.x = x
        tile.y = y
        tile.letter = letter

# Defines a class for a turn.  A turn object gives you the player, the
# tiles used, the squares used on the board, the score of the move,
# and its validity.
class Turn:
    def __init__(turn, player, lettersUsed, squaresUsed, addedScore, validity):
        turn.player = player # The object "player."
        turn.lettersUsed = lettersUsed
        turn.squaresUsed = squaresUsed
        turn.addedScore = addedScore
        # Validity of a turn can be 0, 1, or 2.  0 means invalid.  1
        # means valid.  2 means if you challenge it, you won't lose
        # your turn, but the word won't be taken off the table either.
        turn.validity = validity 

# -------------------------------------------
# Clears the error message
def clearMsg(stdscr, numLines = SCRSIZE_Y - MSG_Y - 1): # numLines = number of lines to clear
    for l in range(numLines):
        for i in range(SCRSIZE_X - MSG_X):
            stdscr.addch(MSG_Y + l, MSG_X + i, " ")

# Prints an error message when player does something bad.  vertOffset = how
# far below MSG_Y the error message is
def printMsg(stdscr, error, vertOffset = 0): 
    assert vertOffset < SCRSIZE_Y - MSG_Y - 1, "Error message off screen"
    stdscr.addstr(MSG_Y + vertOffset, MSG_X, error)

# Redraws the rack, which should happen every time a letter is placed.
def redrawRack(rack, stdscr):
    for i in range(7):
        stdscr.delch(RACK_Y, RACK_X + i)
    for i in range(len(rack)):
        stdscr.addch(RACK_Y, RACK_X + i, rack[i])

# Visually shuffle the rack.
def shuffleRack(rack, stdscr):
    random.shuffle(rack)
    redrawRack(rack, stdscr)

# Display score
def displayScore(players, numPlayers, stdscr):
#    for i in range(30):
#        stdscr.delch(SCORE_Y, SCORE_X + i)
    for i in range(numPlayers):
        stdscr.addstr(SCORE_Y, SCORE_X + 9*i, str(players[i].score))

# Returns "1" if all words are proper Scrabble words, returns 0 if
# they are not.
def verifyWords(words):
    # First, prune word list so that no word appears more than once.
    # This is so the "index" function works correctly.
    prunedList = []
    for word in words:
        if word in prunedList: pass
        else: prunedList.append(word)

    # Each number in the list "check" is 0 or 1, and if it's 0, the
    # corresponding word is invalid, and if it's 1, the corresponding
    # word is valid.  Each word starts "invalid" and becomes valid
    # once it is found in the dictionary.
    check = [0] * len(prunedList)
    
    dictionary.seek(0) # Go to beginning of file
    
    for line in dictionary:
        for word in prunedList:
            expression = "^" + word + "\n" + "$"
            object = re.compile(expression)
            if object.match(line) != None:
                check[prunedList.index(word)] = 1
    
    if check == [1] * len(prunedList): return 1
    else: return 0

# Given a tile and the direction of a word that it's a part of, find
# the coordinates of the first letter of the word.  Also, the last 
# letter of the word.  Note that seek only finds coordinates in one
# direction.
def seek(x0, y0, direction, squares):
    if direction == "horiz":
        xLeft = x0
        xRight = x0
        while xLeft > 0 and squares[(xLeft-1, y0)].letter != "":
            xLeft = xLeft - 1
        while xRight < 14 and squares[(xRight+1, y0)].letter != "":
            xRight = xRight + 1
        return (xLeft, xRight)

    elif direction == "vert":
        yUp = y0
        yDown = y0
        while yDown < 14 and squares[(x0, yDown+1)].letter != "":
            yDown = yDown + 1
        while yUp > 0 and squares[(x0, yUp-1)].letter != "":
            yUp = yUp - 1
        return (yUp, yDown)

    else: raise NameError('Unspecified direction')

# Given a board configuration, return the score.  The board
# configuration specifies the age of every tile, and it returns the
# score associated with all tiles of age 0.  (age 0 means it was
# placed on the square on that particular turn).  Also it finds all
# words generated by a bunch of new tiles.
def findAndScore(squares):
    score = 0
    wordList = []

    # First find which tiles are new
    newTiles = []
    for tuple in squares.keys():
        if squares[tuple].age == 0:
            newTiles.append(squares[tuple])
    
    # Since squares must form a word, we can take two squares and see
    # which coordinate they differ by, and that will give us the
    # direction of the word.  We can count the parallel word, and then
    # count all the perpendicular words.  If there is one square, the
    # direction can be horizontal.

    if len(newTiles) == 1:
        # Check to see what direction it's in, that is, where the old
        # tiles are.  We want to find the start and end of a proposed
        # word both horizontally and vertically, and if the start
        # equals the end, it's not a word.
        horizRange = seek(newTiles[0].x, newTiles[0].y, "horiz", squares)
        vertRange = seek(newTiles[0].x, newTiles[0].y, "vert", squares)
        if horizRange[0] != horizRange[1]:
            direction = "horiz"
        elif vertRange[0] != vertRange[1]:
            direction = "vert"
        else: return 3
    elif len(newTiles) > 1:
        if newTiles[0].x - newTiles[1].x == 0:
            direction = "vert"
        elif newTiles[0].y - newTiles[1].y == 0:
            direction = "horiz"
        else:
            raise NameError('Two squares do not form a line')
    else:
        raise NameError('len(newTiles) < 1')

    # Now we count the parallel word (we can only count this once, we
    # can't count it once for each letter, which is why we have to
    # count it separately).  Make sure to check that tiles form one
    # continuous word.

    # To find the start and end of the word, we use seek:

    wordRange = seek(newTiles[0].x, newTiles[0].y, direction, squares)
    word = ""
    wordScore = 0
    if direction == "horiz":
        # Check that tiles form one continuous word
        for tile in newTiles:
            if tile.x in range(wordRange[0], wordRange[1]+1): pass
            else: return 3
        y = newTiles[0].y

        wordBonus = 1 # Multiply by this at the end - DW, TW
        for x in range(wordRange[0], wordRange[1] + 1):
            # Find the word
            word = word + squares[(x, y)].letter
            # Score the word - count letters first, then once the word
            # is formed, multiply the DW and TW scores in.
            
            letterBonus = 1 # Accounts for DL, TL bonuses
            letterValue = letters.score[squares[(x, y)].letter]
            if squares[(x, y)].age == 0:
                bonus = squares[(x, y)].multiplier
                if bonus == "DW": wordBonus = 2*wordBonus
                elif bonus == "TW": wordBonus = 3*wordBonus
                elif bonus == "DL": letterBonus = 2*letterBonus
                elif bonus == "TL": letterBonus = 3*letterBonus
                else: pass
            wordScore = wordScore + letterValue*letterBonus
        wordScore = wordScore*wordBonus

    elif direction == "vert":
        # Check that tiles form one continuous word
        for tile in newTiles:
            if tile.y in range(wordRange[0], wordRange[1]+1): pass
            else: return 3
        x = newTiles[0].x

        wordBonus = 1 # Multiply by this at the end - DW, TW
        for y in range(wordRange[0], wordRange[1] + 1):
            # Find the word
            word = word + squares[(x, y)].letter
            # Score the word

            letterBonus = 1
            letterValue = letters.score[squares[(x, y)].letter]
            if squares[(x, y)].age == 0:
                bonus = squares[(x, y)].multiplier
                if bonus == "DW": wordBonus = 2*wordBonus
                elif bonus == "TW": wordBonus = 3*wordBonus
                elif bonus == "DL": letterBonus = 2*letterBonus
                elif bonus == "TL": letterBonus = 3*letterBonus
                else: pass
            wordScore = wordScore + letterValue*letterBonus
        wordScore = wordScore*wordBonus
    else: raise NameError('Wrong direction')
    wordList.append(word) # Add parallel word to list of words
    score = score + wordScore

    # Now count perpendicular words in the exact same way!
    for tile in newTiles:
        word = ""
        wordScore = 0
        if direction == "horiz":
            wordRange = seek(tile.x, tile.y, "vert", squares)
            x = tile.x

            wordBonus = 1
            for y in range(wordRange[0], wordRange[1] + 1):
                # Find the word
                word = word + squares[(x, y)].letter
                # Score the word

                letterBonus = 1
                letterValue = letters.score[squares[(x, y)].letter]
                if squares[(x, y)].age == 0:
                    bonus = squares[(x, y)].multiplier
                    if bonus == "DW": wordBonus = 2*wordBonus
                    elif bonus == "TW": wordBonus = 3*wordBonus
                    elif bonus == "DL": letterBonus = 2*letterBonus
                    elif bonus == "TL": letterBonus = 3*letterBonus
                    else: pass
                wordScore = wordScore + letterValue*letterBonus
            wordScore = wordScore*wordBonus

        elif direction == "vert":
            wordRange = seek(tile.x, tile.y, "horiz", squares)
            y = tile.y

            wordBonus = 1
            for x in range(wordRange[0], wordRange[1] + 1):
                # Find the word
                word = word + squares[(x, y)].letter
                # Score the word

                letterBonus = 1
                letterValue = letters.score[squares[(x, y)].letter]
                if squares[(x, y)].age == 0:
                    bonus = squares[(x, y)].multiplier
                    if bonus == "DW": wordBonus = 2*wordBonus
                    elif bonus == "TW": wordBonus = 3*wordBonus
                    elif bonus == "DL": letterBonus = 2*letterBonus
                    elif bonus == "TL": letterBonus = 3*letterBonus
                    else: pass
                wordScore = wordScore + letterValue*letterBonus
            wordScore = wordScore*wordBonus
        
        else: raise NameError('Wrong direction')
        if wordRange[0] != wordRange[1]:
            wordList.append(word) # Add perpendicular word to word list
            score = score + wordScore
    
    # Bingos
    if len(newTiles) == 7:
        score = score + 50
    
    # Now we have counted all the tiles and found all the words!
    return [wordList, score]

# Removes a turn.
def removeTurn(turn, players, numPlayers, squares, stdscr):
    # Reset score
    turn.player.score = turn.player.score - turn.addedScore
    displayScore(players, numPlayers, stdscr)
    # Reset squares
    for square in turn.squaresUsed:
        square.letter = ""
        if (square.x, square.y) in bonus.bonuses.keys():
            color = bonus.colors[square.multiplier]
            stdscr.addch(square.y, square.x, " ", curses.color_pair(color))
        else: stdscr.addch(square.y, square.x, ".", curses.color_pair(1))
    # Reset racks
    for letter in turn.lettersUsed:
        turn.player.rack.append(letter)
    redrawRack(turn.player.rack, stdscr)
    # Subtract from age of tiles
    for tuple in squares.keys():
        if squares[tuple].age > -1:
            squares[tuple].age = squares[tuple].age - 1

# Play the tiles.  Tiles are written as a tile object.
def playTiles(player, tiles, players, numPlayers, squares, stdscr):
    lettersUsed = []
    squaresUsed = []
    # See which letters and squares are being used
    for tile in tiles:
        lettersUsed.append(tile.letter)
        squaresUsed.append(squares[(tile.x, tile.y)])

    # Check that at least one letter has been used
    if len(tiles) < 1: return 3
    # Check that letters are not on top of other letters
    for tile in tiles:
        if squares[(tile.x, tile.y)].letter != "":
            return 3
    # Check that tiles are in a line
    if len(tiles) == 1: direction = "horiz"
    else:
        # If x coordinates are the same
        if tiles[0].x - tiles[1].x == 0:
            direction = "vert"
        # If y coordinates are the same
        elif tiles[0].y - tiles[1].y == 0:
            direction = "horiz"
        else:
            return 3
    if direction == "horiz":
        # Make sure y coordinates are the same
        for tile in tiles:
            if tile.y != tiles[0].y:
                return 3
    elif direction == "vert":
        # Make sure x coordinates are the same
        for tile in tiles:
            if tile.x != tiles[0].x:
                return 3
    else: raise NameError('Wrong direction')
    
    # Check that tiles form one connected word (done in 
    # "findAndScore")
    
    # Check to see if it's the first move.
    firstMove = 1
    for tuple in squares.keys(): 
        if squares[tuple].age > -1: firstMove = 0

    # Check that tiles link to at least one old tile, unless it's the
    # first move.
    link = 0
    for tile in tiles:
        if tile.y + 1 < BOARDSIZE_Y:
            if squares[(tile.x, tile.y+1)].age > -1: link = 1
        if tile.y - 1 >= 0:
            if squares[(tile.x, tile.y-1)].age > -1: link = 1
        if tile.x + 1 < BOARDSIZE_X:
            if squares[(tile.x+1, tile.y)].age > -1: link = 1
        if tile.x - 1 >= 0:
            if squares[(tile.x-1, tile.y)].age > -1: link = 1
    if link == 0 and firstMove == 0: return 3

    # If it's the first move, check to see that the tiles go through
    # the center.
    if firstMove == 1:
        goThroughCenter = 0
        for tile in tiles:
            if tile.x == 7 and tile.y == 7: goThroughCenter = 1
        if goThroughCenter == 0: return 3  # Comment to debug

    # Play word (age 0) and age other tiles
    for tuple in squares.keys():
        if squares[tuple].age > -1:
            squares[tuple].age = squares[tuple].age + 1
    for tile in tiles:
        squares[(tile.x, tile.y)].letter = tile.letter
        squares[(tile.x, tile.y)].age = 0
    
    # Score word
    wordsAndScore = findAndScore(squares)
    wordList = wordsAndScore[0]
    addedScore = wordsAndScore[1]

    player.score = player.score + addedScore
    
    # Display score
    displayScore(players, numPlayers, stdscr)
    
    # Create a turn object and check validity
    if verifyWords(wordList) == 1: validity = 1
    elif verifyWords(wordList) == 0: validity = 0
    else: raise NameError('verifyWords returns neither 1 nor 0')
    newturn = Turn(player, lettersUsed, squaresUsed, addedScore, validity)
    
    # Remove turn if word verification is on and the word is wrong
    if validity == 0 and options.challenge == False:
        removeTurn(newturn, players, numPlayers, squares, stdscr)
        return 4
    else:
        return newturn

# A player takes a turn.  Return a turn object and the "turnCounter"
# (something indicating who is going next).
def oneTurn(previousTurn, player, squares, stdscr, bag, players, numPlayers):
    # Announce whose turn it is
    stdscr.addnstr(TURN_Y, TURN_X, player.name + "'s turn", 70)

    # Give player a rack
    while len(player.rack) < 7 and len(bag) > 0:
        tile = random.choice(bag)
        player.rack.append(tile)
        bag.remove(tile)
    
    tiles = [] # Tiles the player will place on the board this turn
    
    # Display rack
    redrawRack(player.rack, stdscr)

    # Upon inputting a character...
    while 1:
        c = stdscr.getch()
        coords = stdscr.getyx()
        x = coords[1]; y = coords[0]

        # Arrow keys move the cursor (or hjkl)
        if c == curses.KEY_LEFT or c == KEY_H:
            if x == 0: pass
            else: stdscr.move(y, x-1)
        elif c == curses.KEY_RIGHT or c == KEY_L:
            if x >= SCRSIZE_X - 1: pass
            else: stdscr.move(y, x+1)
        elif c == curses.KEY_UP or c == KEY_K:
            if y == 0: pass
            else: stdscr.move(y-1, x)
        elif c == curses.KEY_DOWN or c == KEY_J:
            if y >= SCRSIZE_Y - 1: pass
            else: stdscr.move(y+1, x)
        # yubn moves diagonally (nethack-style)
        elif c == KEY_Y:
            if x == 0 or y == 0: pass
            else: stdscr.move(y-1, x-1)
        elif c == KEY_U:
            if x >= SCRSIZE_X - 1 or y == 0: pass
            else: stdscr.move(y-1, x+1)
        elif c == KEY_B:
            if x == 0 or y >= SCRSIZE_Y - 1: pass
            else: stdscr.move(y+1, x-1)
        elif c == KEY_N:
            if x >= SCRSIZE_X - 1 or y >= SCRSIZE_Y - 1: pass
            else: stdscr.move(y+1, x+1)

        elif c == KEY_BACKSPACE or c == KEY_DEL: # Remove tile from board
            # Ensure that cursor is over a tile, and if so, find the
            # tile
            ourTile = 0
            for tile in tiles:
                if tile.x == x and tile.y == y: ourTile = tile
            
            if ourTile != 0:
                # Repaint square on board
                if (x, y) in bonus.bonuses.keys():
                    color = bonus.colors[squares[(x, y)].multiplier]
                    stdscr.addch(y, x, " ", curses.color_pair(color))
                else: stdscr.addch(y, x, ".", curses.color_pair(1))
                # Remove tile from tile list
                tiles.remove(ourTile)
                # Add tile to rack
                player.rack.append(ourTile.letter)
                redrawRack(player.rack, stdscr)
                stdscr.move(y, x)

        elif c == KEY_SPACE or c == KEY_S: # Space or "s" - shuffle tiles
            shuffleRack(player.rack, stdscr)
            stdscr.move(y, x)
        # Once a player presses Enter, that's like inputting a command.
        # Deal with commands accordingly.
        elif c == KEY_NEWLINE: # New line - submit data
            # Submit word
            if onBoard(x, y):
                a = playTiles(player, tiles, players, numPlayers, squares, stdscr)
                if a == 3: # User has made an error
                    turnObject = previousTurn 
                    turnCounter = player
                    # Remove stuff from the board
                    for tile in tiles:
                        if (tile.x, tile.y) in bonus.bonuses.keys():
                            color = bonus.colors[squares[(tile.x, tile.y)].multiplier]
                            stdscr.addch(tile.y, tile.x, " ", \
                            curses.color_pair(color))
                        else: stdscr.addch(tile.y, tile.x, ".", \
                        curses.color_pair(1))
                        player.rack.append(tile.letter)
                    tiles = []
                    redrawRack(player.rack, stdscr)
                elif a == 4: # User has made an invalid word (we need
                # a separate case because if this has happened the rack
                # has already been removed)
                    turnObject = previousTurn
                    turnCounter = player
                    tiles = []
                else:
                    turnObject = a
                    if player.index < numPlayers - 1:
                        turnCounter = players[player.index + 1]
                    elif player.index == numPlayers - 1:
                        turnCounter = players[0]
                    else:
                        raise NameError('Unknown player index')
                break

            # Shuffle rack
            elif onShuffleButton(x, y):
                shuffleRack(player.rack, stdscr)
                stdscr.move(SHUFFLE_Y, SHUFFLE_X)
            # Recall tiles
            elif onRecallButton(x, y):
                for tile in tiles:
                    if (tile.x, tile.y) in bonus.bonuses.keys():
                        color = bonus.colors[squares[(tile.x, \
                        tile.y)].multiplier]
                        stdscr.addch(tile.y, tile.x, " ", \
                        curses.color_pair(color))
                    else: stdscr.addch(tile.y, tile.x, ".", \
                    curses.color_pair(1))
                    player.rack.append(tile.letter)
                tiles = []
                redrawRack(player.rack, stdscr)
                stdscr.move(RECALL_Y, RECALL_X)
            # Exchange tiles
            elif onPassButton(x, y):
                if len(bag) >= 7:
                    # Skip your turn
                    if player.index == numPlayers - 1:
                        turnCounter = players[0]
                    else: turnCounter = players[player.index + 1]
                    turnObject = Turn(player, [], [], 0, 2)
                    printMsg(stdscr, "Exchange tiles:")
                    printMsg(stdscr, "(press Enter when done or Esc to cancel)", vertOffset = 1)
                    exchange = []
                    while 1:
                        c = stdscr.getch()
                        if c == KEY_NEWLINE: # New line - submit exchanged tiles
                            # Now add tiles from the bag
                            while len(player.rack) < 7:
                                tile = random.choice(bag)
                                player.rack.append(tile)
                                bag.remove(tile)
                            for tile in exchange:
                                bag.append(tile)
                            # Now erase the exchange messages from
                            # the screen
                            clearMsg(stdscr)
                            break
                        
                        elif c == KEY_BACKSPACE or c == KEY_DEL: # Backspace - delete a tile
                            if len(exchange) > 0:
                                stdscr.delch(21, 50 + len(exchange) - 1)
                                tile = exchange.pop()
                                player.rack.append(tile)
                        elif c == KEY_ESC: # Esc (Escape) - don't exchange
                            turnCounter = player
                            turnObject = previousTurn
                            for tile in exchange:
                                player.rack.append(tile)
                            exchange = []
                            clearMsg(stdscr)
                            break
                        else:
                            if player.rack.count(chr(c)) > 0:
                                stdscr.addch(21, 50 + len(exchange), chr(c))
                                exchange.append(chr(c))
                                player.rack.remove(chr(c))
                        redrawRack(player.rack, stdscr)
                    break
                else: 
                    stdscr.addstr(21, 34, "Less than 7 tiles left in bag")
                stdscr.move(PASS_Y, PASS_X)
    
            # Undo the last turn (so that it is once again the
            # previous player's turn)
            elif onUndoButton(x, y):
                removeTurn(previousTurn, players, numPlayers, squares, stdscr)
                turnCounter = previousTurn.player
                turnObject = Turn(previousTurn.player, [], [], 0, 2)
                stdscr.move(UNDO_Y, UNDO_X)
                break
                
            # Challenge the last turn
            elif onChallengeButton(x, y):
                if previousTurn.validity == 0:
                # Player uses his turn to invalidate the other's move,
                # then takes another turn
                    removeTurn(previousTurn, players, numPlayers, squares, stdscr)
                    turnCounter = player
                    turnObject = Turn(player, [], [], 0, 2)
                elif previousTurn.validity == 1:
                    # Player doesn't get a turn if the challenged word
                    # is valid
                    if player.index == numPlayers - 1:
                        turnCounter = players[0]
                    else: turnCounter = players[player.index + 1]
                    turnObject = Turn(player, [], [], 0, 2)
                elif previousTurn.validity == 2:
                # Then just go on as usual, nobody loses his turn.
                    turnCounter = player
                    turnObject = Turn(player, [], [], 0, 2)
                else: raise NameError('Validity not 0, 1, or 2')
                stdscr.move(CHALLENGE_Y, CHALLENGE_X)
                break

            # Quit the game
            elif onQuitButton(x, y):
                turnObject = previousTurn
                turnCounter = 0
                stdscr.move(QUIT_Y, QUIT_X)
                break
        elif c == KEY_Q and (not onBoard(x, y)): # the letter "q"
            turnObject = previousTurn
            turnCounter = 0
            stdscr.move(QUIT_Y, QUIT_X)
            break

        else: # If on the board, assume he is adding tiles
            if onBoard(x, y):
                # Make sure tile is in rack and you are adding to a
                # blank space
                if chr(c) in player.rack and squares[(x, y)].age == -1:
                    player.rack.remove(chr(c))
                    redrawRack(player.rack, stdscr)
                    tiles.append(Tile(x, y, chr(c)))
                    stdscr.addch(y, x, chr(c), curses.color_pair(1))
            else:
                pass
    # Announce whose turn it isn't
    for i in range(SCRSIZE_X - TURN_X):
        stdscr.addch(TURN_Y, TURN_X + i, " ")
    
    return [turnObject, turnCounter]        

# This runs the game.
def newGame():
    random.seed()
    # Initialize squares
    squares = {} # Create a dictionary.
    for x in range(15):
        for y in range(15):
            if (x, y) in bonus.bonuses.keys(): # if they are bonus squares
                # Note that once a tile is placed on the board, the
                # multiplier will be set to 1.
                squares[(x, y)] = Square(x, y, bonus.bonuses[(x, y)])
            else:
                squares[(x, y)] = Square(x, y, 1)

    # Initialize players
    players = []
    print "Welcome to command-line Scrabble!"
    try:
        numPlayers = int(raw_input("Please enter the number of players. "))
        if numPlayers < 2 or numPlayers > 4:
            print "Scrabble is a game for 2-4 people"
            return 2
    except ValueError:
        print "Must enter a number"
        return 2
    for i in range(numPlayers):
        name = raw_input("Enter name of player " + str(i+1) + ": ")
        players.append(Player(name))
    random.shuffle(players)

    for i in range(numPlayers-1):
        players[i].index = i
    players[numPlayers-1].index = numPlayers-1
    
    # Initialize tiles in bag
    bag = []
    for letter in letters.frequency.keys():
        i = letters.frequency[letter]
        while i > 0:
            bag.append(letter)
            i = i - 1

    # Draws board and sidebar
    stdscr = curses.initscr()
    curses.noecho(); curses.cbreak(); stdscr.keypad(1)
    stdscr.resize(24, 80) # Standardize window size
    curses.start_color()

    # Initialize color pairs
    # Normal squares
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # DL = cyan background
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_CYAN)
    # TL = blue background
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLUE)
    # DW = red background
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_RED)
    # TW = magenta background
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_MAGENTA)

    # Squares' original symbols
    for i in range(15):
        for j in range(15):
            if (i, j) in bonus.bonuses.keys(): # Color bonus squares
                color = bonus.colors[squares[(i, j)].multiplier]
                stdscr.addch(j, i, " ", curses.color_pair(color))
            else: stdscr.addch(j, i, ".", curses.color_pair(1))
    
    # Make column 16 and row 16 stand out
    for i in range(80):
        stdscr.addch(16, i, " ", curses.A_STANDOUT)
    for j in range(16):
        stdscr.addch(j, 16, " ", curses.A_STANDOUT)

    # Rack is at row 19, column 15.  Do not make rack until a player's
    # turn starts.
    stdscr.addstr(19, 4, "Your rack:")

    # Row 21: SHUFFLE  RECALL  PASS/EXCHANGE
    stdscr.addstr(21, 2, "SHUFFLE", curses.A_STANDOUT)
    stdscr.addstr(21, 11, "RECALL", curses.A_STANDOUT)
    stdscr.addstr(21, 19, "PASS/EXCHANGE", curses.A_STANDOUT)

    # Column 20 row 5: UNDO/CHALLENGE/QUIT
    stdscr.addstr(5, 20, "UNDO", curses.A_STANDOUT)
    stdscr.addstr(7, 20, "CHALLENGE", curses.A_STANDOUT)
    stdscr.addstr(9, 20, "QUIT", curses.A_STANDOUT)

    # Column 18-25, 27-34 etc. are players (Row 1).  Row 2 is scores.
    for i in range(numPlayers):
        stdscr.addnstr(1, 18 + 9*i, players[i].name, 8)
    displayScore(players, numPlayers, stdscr)
   
    # Begins game
    def isGameOver(): # Determines if the game is over
        status = 0
        for player in players:
            if player.rack == [] and bag == []:
                status = 1
        return status

    turnCounter = players[0] # Person whose turn it is to play next
    turnObject = Turn(players[0], [], [], 0, 2) # "Previous turn"
    # Game loop
    while isGameOver() == 0 and turnCounter != 0:
        turnObjectCounter = oneTurn(turnObject, turnCounter, squares, stdscr, bag, players, numPlayers)
        turnObject = turnObjectCounter[0]
        turnCounter = turnObjectCounter[1]
    
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()

# -------------------------------------------

newGame() # Runs the game

dictionary.close()

