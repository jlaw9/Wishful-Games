#! /usr/bin/env python

from optparse import OptionParser
import sys
from copy import copy, deepcopy

def main(num_players, num_rows, num_cols, debug):
    gameboard = GameBoard(num_players, num_rows, num_cols, debug)
    print "\nNumber of players: %d, size of board: %d by %d\n" % (num_players, num_rows, num_cols)
    print "Use 'undo' to undo the previous turn. Can only take back one turn"
    gameboard.print_board()
    curr_player = 1
    # keep taking turns until someone wins
    while True:
        # keep looping until the user enters a valid input
        while True:
            try:
                if debug:
                    print ""
                    if curr_player == 1:
                        player_input = "1,1"
                    elif curr_player == 2:
                        player_input = "9,9"
                else:
                    player_input = raw_input("%s: enter a 'row,col' to add slime to: " % gameboard.print_player_color(curr_player, "Player %d" %(curr_player)))
                # allow the user to undo a move
                if player_input == "undo":
                    curr_player = gameboard.undo()
                    continue
                row,col = player_input.rstrip().split(',')
                row = int(row) - 1
                col = int(col) - 1
            except ValueError:
                print "Please enter a valid 'row,col' for example: 1,1. Entered: ", player_input.rstrip()
                continue
            if row < 0 or row >= num_rows or col < 0 or col >= num_cols:
                print "%d,%d not a valid square. Please enter a valid square" % (row+1, col+1)
            elif gameboard.take_turn(curr_player, row, col) == -1:
                owner = gameboard.board[row][col].player
                print "square owned by %s. Please choose a different square" % \
                (gameboard.print_player_color(owner, "Player %d" %(owner)))
                debug = False
            else:
                break
        # switch players
        curr_player = gameboard.next_player()


class GameBoard:
    # build the game board
    def __init__(self, num_players, num_rows, num_cols, debug=False):
        self.players = range(1,num_players+1)
        self.prev_players = list(self.players)
        self.board = self.build_board(num_rows, num_cols)
        self.prev_board = list(self.board)
        # the number of turns taken so far
        self.num_turns = 0
        self.debug = debug
        self.curr_player = 1
        self.prev_player = self.curr_player
        self.player_colors = {
                1:"LBLUE",
                2:"LPURPLE",
                3:"LCYAN",
                4:"LGREEN",
                5:"LYELLOW",
                6:"GREEN",
                7:"YELLOW",
                8:"BLUE",
                9:"PURPLE",
                10:"CYAN",
                11:"DGRAY",
                None:"NC",
                }
        self.colors = {
                "BLACK":'\033[0;30m',
                "DGRAY":'\033[1;30m',
                "RED":'\033[0;31m',
                "LRED":'\033[1;31m',
                "GREEN":'\033[0;32m',
                "LGREEN":'\033[1;32m',
                "YELLOW":'\033[0;33m',
                "LYELLOW":'\033[1;33m',
                "BLUE":'\033[0;34m',
                "LBLUE":'\033[1;34m',
                "PURPLE":'\033[0;35m',
                "LPURPLE":'\033[1;35m',
                "CYAN":'\033[0;36m',
                "LCYAN":'\033[1;36m',
                "LGRAY":'\033[0;37m',
                "WHITE":'\033[1;37m',
                "NC":'\033[0m', # No Color
                }
        #for player in self.player_colors:
        #    print self.print_player_color(player, player)

    def build_board(self, num_rows, num_cols):
        # number of rows and colums the board should have
        # the limit of corners should be 1
        # the limit of the boandaries is 2
        # rest is 3
        board = [[0 for col in range(num_cols)] for row in range(num_rows)]
        for row in range(num_rows):
            for col in range(num_cols):
                neighbors = []
                # find the neighbors of the square
                # the limit is 1 - # of neighbors
                if row-1 >= 0: 
                    neighbors.append((row-1, col))
                if row+1 < num_rows: 
                    neighbors.append((row+1, col))
                if col-1 >= 0: 
                    neighbors.append((row, col-1))
                if col+1 < num_cols: 
                    neighbors.append((row, col+1))
                limit = len(neighbors)-1
                # initialize the square objects in each square of the board
                board[row][col] = Square(limit, neighbors)

        return board

    
    def print_board(self):
        #out = []
        out = ["  " + " ".join([str(x) for x in range(1,len(self.board[0])+1)])]
        for row in range(len(self.board)):
            # TODO add a color to the square
            line = str(row+1) + " " + "|".join([self.print_player_color(square.player, square.current_slime) for square in self.board[row]])
            #line = "|".join([str(square.current_slime) for square in row])
            #line += '\t' + "|".join(["P%s" % (str(square.player) if square.player is not None else '-') for square in row])
            out.append(line)
        print '\n'.join(out)

    def print_player_color(self, player, text):
        color = self.player_colors[player]
        return self.colors[color] + str(text) + self.colors['NC']
        #return str(text)

    def next_player(self):
        #print "curr player was:", self.curr_player
        #next_player_index = ((self.curr_player) % len(self.players))
        curr_player_index = self.players.index(self.curr_player)
        next_player_index = (curr_player_index + 1) % len(self.players)
        self.curr_player = self.players[next_player_index]
        #print "curr player is:", self.curr_player
        return self.curr_player

    def take_turn(self, player, row, col):
        # keep track of everything before this turn was taken to be able to undo a turn
        self.prev_player = self.curr_player
        self.prev_players = list(self.players)
        #self.prev_board = [x[:] for x in self.board]
        self.prev_board = deepcopy(self.board)

        self.num_turns += 1
        #explode = self.board[row][col].add_slime(player)
        result = self.add_slime_and_explode(player, row, col, slime=1, takeover=False)
        if result == -1:
            return -1
        # print the board 
        self.print_board()
        # check if there's a winner
        self.check_winner()

    def undo(self):
        # set everything to the previous turns settings
        self.curr_player = self.prev_player
        self.players = list(self.prev_players)
        self.board = deepcopy(self.prev_board)
        #self.board = [row[:] for row in self.prev_board]
        self.num_turns = self.num_turns - 1
        # print the board 
        self.print_board()
        
        return self.curr_player

    # recursive function to explode
    def add_slime_and_explode(self, player, row, col, slime=1, takeover=False, recursion_depth=0):
        if takeover:
            self.board[row][col].player = player
        # TODO keep the recursion from going to deep and breaking the game
        # try to set a recursion_depth limit to prevent from over-exploding the board?
        if recursion_depth > 500:
            self.board[row][col].current_slime = self.board[row][col].limit - 1
            if self.debug:
                print "hit recursion limit (6). returning"
            return
        explode = self.board[row][col].add_slime(player, slime)
        if explode == -1:
            return -1
        if explode:
            #print "%d,%d is exploding %d slime to its neighbors!" % (row, col, self.board[row][col].limit)
            print "%d,%d is exploding!" % (row+1, col+1)
            for rown, coln in self.board[row][col].neighbors:
                #slime = self.board[row][col].limit - 1
                #if self.board[row][col].limit > self.board[rown][coln].limit:
                #    slime = self.board[rown][coln].limit - 1
                #if slime == 0:
                slime = 1
                self.add_slime_and_explode(player, rown, coln, slime, takeover=True, recursion_depth=recursion_depth+1)

    def check_winner(self):
        if self.num_turns > len(self.players):
            curr_players = set()
            for row in self.board:
                for square in row:
                    if square.player is not None:
                        curr_players.add(square.player)

            # remove players that aren't on the board anymore
            for player in self.players:
                if player not in curr_players:
                    print self.print_player_color(player, "Player %d ELIMINATED" % player)
            self.players = list(sorted(curr_players))

            # game is over if there are no more players
            if len(self.players) == 1:
                winner = list(curr_players)[0]
                print self.print_player_color(winner, "Player %d WINS!!!" % winner)
                sys.exit()


class Square:
    # This is the object of the square of the board
    def __init__(self, limit, neighbors):
        """ limit: limit of slime 
        neighbors: list of row, column neighbor tuples 
        """
        self.limit = limit
        self.neighbors = neighbors
        self.current_slime = 0
        self.player = None

    # if the square contains more slime than it can hold, then it will explode slime equal to 1-limit to its neighbors. 
    # when exploding out, the player takes over the neighboring squares, and each of those have a possibility to explode.
    # sets the current_slime to 0
    def explode(self):
        self.current_slime = 0
        self.player = None

    def check_limit(self):
        if self.current_slime > self.limit:
            self.explode()
            return True
        else:
            return False

    def add_slime(self, player, slime=1):
        # more than one amount of slime can be added if an explosion occurs
        if self.player is None:
            self.player = player
        if self.player != player:
            #print "Illegal move: ", self.player, " != ", player
            return -1
        else:
            self.current_slime += slime
            return self.check_limit()

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option('-p', "--num-players", type='int', default=2, 
            help="Number of players to play with")
    parser.add_option('-r', "--num-rows", type='int', default=4, 
            help="Number of rows for the board")
    parser.add_option('-c', "--num-cols", type='int', default=5, 
            help="Number of columns for the board")
    parser.add_option('-d', "--debug", action='store_true',
            help="Run a game simulation for debugging")

    opts, args = parser.parse_args()
    
    main(opts.num_players, opts.num_rows, opts.num_cols, opts.debug)
