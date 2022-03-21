import logging
import random
#import pygame
import sys

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

def inside(board, x, y):
	# bounds
	if x < 0 or y < 0:
		return False
	if x > len(board)-1 or y > len(board[0])-1:
		return False

	# empty space designates non-painted space
	if board[x][y] is " ":
		return True
	else:
		return False

def set_node(board, x, y):
	# TODO: check n,s,e,w for mines and set number
	board[x][y] = "."

def flood_fill(board, x, y):
	if not inside(board, x, y):
		return

	set_node(board, x, y)

	# south, north, west, east
	flood_fill(board, x+1, y)
	flood_fill(board, x-1, y)
	flood_fill(board, x, y-1)
	flood_fill(board, x, y+1)

def reveal_tile(board, player):
	if board[player.x][player.y] == "*":
		print("you died")
		exit()

	# flood fill traversal
	# TODO: recursive traversal is ineffecient.
	# re-implement with a better flood fill
	x = player.x
	y = player.y
	
	flood_fill(board, x, y)

	# expanding search to find mine borders

def print_board(board, player):
	GRID = (len(board),len(board[0]))

	MINE_ICON = "{}"

	print(" ", end="")
	for i in range(GRID[0]):
		print("--", end="")
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
			if j_val == "*":
				print_token = MINE_ICON

			if i == player.x and j == player.y:
				print_token = colored_background_yellow(print_token)
#			else:
#				print_token = colored_background_green(print_token)
			#print("{} ".format(print_token),end="")
			print(print_token,end="")
		print("|")
	
	print(" ", end="")
	for i in range(GRID[0]):
		print("--",end="")
	print()

def generate_mines(board, num_mines):
	for num_mine in range(num_mines):
		rand_i = random.randint(0, len(board)-1)
		rand_j = random.randint(0, len(board[0])-1)
		logging.info("generating {} of {} at ({}, {})".format(num_mine, num_mines, rand_i, rand_j))
		
		#  check this space to make sure it's not
		# already a mine
		while board[rand_i][rand_j] is "*":
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
		board[rand_i][rand_j] = "*"

class Player():
	def __init__(self, board):
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

logging.basicConfig(filename="mine.log", level=logging.INFO)
logging.info(" ")
logging.info("started minesweeper")

MINES = 50
GRID = (10,10)

board = [[" " for x in range(GRID[0])] for i in range(GRID[1])]

player = Player(board)

print_board(board, player)

generate_mines(board, MINES)

print_board(board, player)

num_moves = 10


while num_moves > 0:
	logging.info("num_moves: {}".format(num_moves))
	direction = input("--> ")
	
	# no char input means player is making this selection
	if direction == "":
		reveal_tile(board, player)

	# check for a direction or a flag
	else:
		direction = direction[0]
		if direction == 'a':
			player.move_left()
		if direction == 's':
			player.move_down()
		if direction == 'w':
			player.move_up()
		if direction == 'd':
			player.move_right()
		if direction == 'f':
			num_moves -= 1

	print_board(board, player)

logging.info("finished minesweeper")
logging.info(" ")
