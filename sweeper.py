import logging
import random
#import pygame
import sys
import os
import argparse

def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

def colored_background_reset(text):
	return "{}\u001b[0m".format(text)

def colored_background_black(text):
    return colored_background_reset("\u001b[40m{}".format(text))

def colored_background_red(text):
    return colored_background_reset("\u001b[41m{}".format(text))

def colored_background_green(text):
    return colored_background_reset("\u001b[42m{}".format(text))

def colored_background_yellow(text):
    return colored_background_reset("\u001b[43m{}".format(text))

MINE = "*"
FLAG = "f"
UNKNOWN = "."
BLANK = " "

def inside(board, solution_board, x, y):
	# bounds
	if x < 0 or y < 0:
		return False
	if x >= len(solution_board) or y >= len(solution_board[0]):
		return False

	# if we've already resolved this, we can treat it as false
	if board[x][y] != UNKNOWN:
		return False

	# mine will be false
	tile = solution_board[x][y]
	if tile == MINE:
		return false
	
	# we'll handle a number or a blank outside of this function, I guess
	return tile
		

def flood_fill(board, solution_board, x, y):
#	print_board(board, None)
	set_value = inside(board, solution_board, x, y)
	if set_value is not False:
		# 	 if we're still looking at a fillable value,
		# ie a '.', then we can continue filling here
		board[x][y] = set_value
		if set_value == BLANK:
			# south, north, west, east
			flood_fill(board, solution_board, x+1, y)
			flood_fill(board, solution_board, x-1, y)
			flood_fill(board, solution_board, x, y-1)
			flood_fill(board, solution_board, x, y+1)

def reveal_tile(board, solution_board, player):
	if solution_board[player.x][player.y] == MINE:
		print_board(board, player, mine_icon=colored_background_red("{}"), message="YOU DIED LIKE A BITCH.")
		player.num_moves = 0
		return

	# flood fill traversal
	# TODO: recursive traversal is ineffecient.
	# re-implement with a better flood fill
	x = player.x
	y = player.y
	
	flood_fill(board, solution_board, x, y)

	# expanding search to find mine borders
def check_mine(board, x, y):
	# bounds checks
	if x < 0 or y < 0:
		return 0
	if x >= len(board) or y >= len(board[0]):
		return 0

	# check if this tile is a mine
	if board[x][y] == "*":
		return 1
	else:
		return 0

def count_surrounding_mines(board, x, y):
	mine_count = 0

	mine_count += check_mine(board, x-1, y-1)
	mine_count += check_mine(board, x-1, y)
	mine_count += check_mine(board, x-1, y+1)

	mine_count += check_mine(board, x, y-1)
	mine_count += check_mine(board, x, y)
	mine_count += check_mine(board, x, y+1)

	mine_count += check_mine(board, x+1, y-1)
	mine_count += check_mine(board, x+1, y)
	mine_count += check_mine(board, x+1, y+1)
	
	return mine_count
	

def resolve_board(board):
	for x in range(len(board)):
		for y in range(len(board[0])):
			# skip over mines
			if board[x][y] == MINE:
				continue
				
			mine_count = count_surrounding_mines(board, x, y)
			#   assign a number or . to our mine count for this tile
			# we're keeping our values in strings for
			# 1) consistency
			# 2) because we're awful programmers
			if mine_count == 0:
				tile_value = BLANK
			else:
				tile_value = str(mine_count)

			board[x][y] = tile_value
				

def print_board(board, player, flag_colors = None, flag_icon = "|^", mine_icon = "{} ".format(UNKNOWN), message=""):
	GRID = (len(board),len(board[0]))
	MINE_ICON = mine_icon
	FLAG_ICON = flag_icon
	print(" ", end="")
	print(message, end="")
	for i in range( (GRID[0]*2) -len(message) ):
		print("-", end="")
	print()
	
	for i, i_val in enumerate(board):
		print("|",end="")
		for j, j_val in enumerate(i_val):
			#  this will preserve the item at this tile
			# but add a whitespace
			print_token = "{} ".format(j_val)
#			print_token = "  ".format(j_val)

			#  this will replace a mine with a two width MINE_ICON
			# insted of the * because our player width is two
			if j_val == MINE:
				print_token = MINE_ICON
			if j_val == FLAG:
				print_token = FLAG_ICON
				if i != player.x or j != player.y:
					print_token = colored_background_yellow(print_token)

			if player is not None:
				if i == player.x and j == player.y:
					print_token = colored_background_green(print_token)
#			else:
#				print_token = colored_background_green(print_token)
			#print("{} ".format(print_token),end="")
			print(print_token,end="")
		print("|")
	
	print(" ", end="")
	mines_message = "-- {} Mines remain ".format(player.num_moves)
	print(mines_message, end="")
	for i in range( (GRID[0]*2) - len(mines_message)):
		print("-",end="")
	print()
	print()

def generate_mines(board, num_mines):
	for num_mine in range(num_mines):
		rand_i = random.randint(0, len(board)-1)
		rand_j = random.randint(0, len(board[0])-1)
		logging.info("generating {} of {} at ({}, {})".format(num_mine, num_mines, rand_i, rand_j))
		
		#  check this space to make sure it's not
		# already a mine
		while board[rand_i][rand_j] is MINE:
			logging.info("  new pos  {} of {} at ({}, {})".format(num_mine, num_mines, rand_i, rand_j))
			#  we'll fill in the next available
			# space with a mine
			rand_i += 1

			# check for bounds, and wrap if appropriate
			if rand_i == len(board):
				rand_i = 0
				rand_j += 1
				if rand_j == len(board[0]):
					rand_j = 0
		board[rand_i][rand_j] = MINE 

class Player():
	def __init__(self, board, num_mines):
		self.num_moves = num_mines
		self.x = 0
		self.y = 0
		self.max_i = len(board)
		self.max_j = len(board[0])
		logging.info("player initialized at {}, {}".format(self.x, self.y))

	def move_right(self):
		if self.y < self.max_j-1:
			self.y += 1
		logging.info("player moved to {}, {}".format(self.x, self.y))
	
	def move_down(self):
		if self.x < self.max_i-1:
			self.x += 1
		logging.info("player moved to {}, {}".format(self.x, self.y))

	def move_left(self):
		if self.y > 0:
			self.y -= 1
		logging.info("player moved to {}, {}".format(self.x, self.y))

	def move_up(self):
		if self.x > 0:
			self.x -= 1
		logging.info("player moved to {}, {}".format(self.x, self.y))

if os.name == 'nt':
	os.system('color')

parser = argparse.ArgumentParser(description='minesweeper - accepts size and num mines as args')
parser.add_argument('-s', '--size', type=int, help='A number to set the size of the gameboard', default=20)
parser.add_argument('-m', '--mines', type=int, help='A number to set the number of mines in the game', default=20)

args = parser.parse_args()

if args.mines > (args.size * args.size):
	print("too mane mines for gameboard size")
	exit(5)

logging.basicConfig(filename="mine.log", level=logging.INFO)
logging.info(" ")
logging.info("started minesweeper")

NUM_MINES = args.mines
GRID = (args.size,args.size)

board = [[UNKNOWN for x in range(GRID[0])] for i in range(GRID[1])]
solution_board = [[UNKNOWN for x in range(GRID[0])] for i in range(GRID[1])]

player = Player(board, NUM_MINES)

generate_mines(board, NUM_MINES)


for x, board_row in enumerate(board):
	for y, board_tile in enumerate(board_row):
		solution_board[x][y] = board_tile

resolve_board(solution_board)

print_board(board, player)

print_solution = False

while player.num_moves > 0:
	if print_solution:
		print_solution = False
		print_board(solution_board, player, message="SOLUTION BOARD", mine_icon="* ")
	else:
		print_board(board, player)

	logging.info("num_moves: {}".format(player.num_moves))
	direction = input("--> ")
	
	# no char input means player is making this selection
	if direction == "":
		reveal_tile(board, solution_board, player)

	# check for a direction or a flag
	else:
		if direction == 'a':
			player.move_left()
		if direction == 's':
			player.move_down()
		if direction == 'w':
			player.move_up()
		if direction == 'd':
			player.move_right()
		if direction == 'f':
			if board[player.x][player.y] == FLAG:
				revert = UNKNOWN
				if solution_board[player.x][player.y] == MINE:
					revert = MINE
				board[player.x][player.y] = revert
				player.num_moves += 1
			elif board[player.x][player.y] == UNKNOWN or board[player.x][player.y] == MINE:
				board[player.x][player.y] = FLAG
				player.num_moves -= 1

		if direction == 'r':
			print_solution = True

logging.info("finished minesweeper")
logging.info(" ")
