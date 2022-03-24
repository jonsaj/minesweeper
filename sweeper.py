import logging
import random
import os
import argparse
from enum import Enum

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

UNKNOWN = "."
MINE = "*"
FLAG = "f"
BLANK = " "
			

class Player():
	def __init__(self):
		self.x = 0
		self.y = 0
		logging.info("player initialized at {}, {}".format(self.x, self.y))

class Direction(Enum):
	UP = 'w'
	DOWN = 's'
	LEFT = 'a'
	RIGHT = 'd'

class Game():
	def __init__(self, size = 10, num_mines = None):

		# initialize with a default player
		self.player = Player()
		self.game_running = True
		self.player_lost = False
		self.player_won = False
		self.game_message = ""
		self.debug_render_bool = False

		if num_mines is None:
			num_mines = size
		self.num_mines = num_mines
		self.num_flags_remaining = self.num_mines
		self.num_revealed_tiles = 0

		# create 2d board
		self.solution_board = [[UNKNOWN for x in range(size)] for i in range(size)]
		self.game_state_board = [[UNKNOWN for x in range(size)] for i in range(size)]
		self.__generate_mines()
		self.__resolve_board()

	def __total_revealable_tiles(self):
		return (len(self.solution_board) * len(self.solution_board[0])) - self.num_mines

	def enable_debug_render(self):
		self.debug_render_bool = True

	def render(self):
		if self.player_won:
			self.game_message = "wow. pretty cool. you won."

		if self.debug_render_bool:
			self.__print_board(self.solution_board, self.player, message="SOLUTION BOARD", mine_icon = "* ")
			self.debug_render_bool = False
		else:
			self.__print_board(self.game_state_board, self.player, message=self.game_message, mine_icon = colored_background_red("* "))
			self.game_message = ''

	def __print_board(self, board, player, flag_colors = None, flag_icon = "|^", mine_icon = "{} ".format(UNKNOWN), message=""):
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
		mines_message = "-- {} Flags remain ".format(self.num_flags_remaining)
		print(mines_message, end="")
		for i in range( (GRID[0]*2) - len(mines_message)):
			print("-",end="")
		print()
		print()



	def exit(self):
		self.game_running = False

	def __generate_mines(self):
		for this_mine in range(self.num_mines):

			# generate a random x,y for this new mine
			rand_x = random.randint(0, len(self.solution_board)-1)
			rand_y = random.randint(0, len(self.solution_board[0])-1)
			logging.info("generating {} of {} at ({}, {})".format(this_mine, self.num_mines, rand_x, rand_y))

			#  check this space to make sure it's not
			# already a mine, incremenenting its position if
			# already a mine at this x,y
			while self.solution_board[rand_x][rand_y] is MINE:
				logging.info("  new pos  {} of {} at ({}, {})".format(this_mine, self.num_mines, rand_x, rand_y))
				#  we'll fill in the next available
				# space with a mine
				rand_x += 1

				# check for bounds, and wrap if appropriate
				if rand_x == len(self.solution_board):
					rand_x = 0
					rand_y += 1
					if rand_y == len(self.solution_board[0]):
						rand_y = 0
			self.solution_board[rand_x][rand_y] = MINE 

	# expanding search to find mine borders
	def __check_mine(self, x, y):
		# bounds checks
		if x < 0 or y < 0:
			return 0
		if x >= len(self.solution_board) or y >= len(self.solution_board[0]):
			return 0

		# check if this tile is a mine
		if self.solution_board[x][y] == "*":
			return 1
		else:
			return 0


	def __count_surrounding_mines(self, x, y):
		mine_count = 0

		# check 9 spaces around our current position
		mine_count += self.__check_mine(x-1, y-1)
		mine_count += self.__check_mine(x-1, y)
		mine_count += self.__check_mine(x-1, y+1)

		mine_count += self.__check_mine(x, y-1)
		mine_count += self.__check_mine(x, y)
		mine_count += self.__check_mine(x, y+1)

		mine_count += self.__check_mine(x+1, y-1)
		mine_count += self.__check_mine(x+1, y)
		mine_count += self.__check_mine(x+1, y+1)

		return mine_count


	def __resolve_board(self):
		for x in range(len(self.solution_board)):
			for y in range(len(self.solution_board[0])):
				# skip over mines
				if self.solution_board[x][y] == MINE:
					continue

				mine_count = self.__count_surrounding_mines(x, y)
				#   assign a number or . to our mine count for this tile
				# we're keeping our values in strings for
				# 1) consistency
				# 2) because we're awful programmers
				if mine_count == 0:
					tile_value = BLANK
				else:
					tile_value = str(mine_count)

				self.solution_board[x][y] = tile_value

	def move_player(self, direction):
		if direction == Direction.RIGHT:
			if self.player.y < len(self.solution_board[0]):
				self.player.y += 1
		elif direction == Direction.DOWN:
			if self.player.x < len(self.solution_board):
				self.player.x += 1
		elif direction == Direction.LEFT:
			if self.player.y > 0:
				self.player.y -= 1
		elif direction == Direction.UP:
			if self.player.x > 0:
				self.player.x -= 1
		else:
			logging.info("invalid player direction")

		logging.info("player moved to {}, {}".format(self.player.x, self.player.y))

	#  Returns False if we are outside of our area
	#    otherwise, will return a tile value:
	#   if we are inside our fillable area, will return BLANK
	#   if we are on the perimiter of our fillable area, will
	#    return the number of surrounding mines
	def __inside(self, x, y):
		# bounds
		if x < 0 or y < 0:
			return False
		if x >= len(self.solution_board) or y >= len(self.solution_board[0]):
			return False

		# if we've already resolved this, we can treat it as false
		if self.game_state_board[x][y] != UNKNOWN:
			return False

		# a located mine will return false
		tile = self.solution_board[x][y]
		if tile == MINE:
			return False

		# we'll handle a number or a blank outside of this function, I guess
		# TODO: I dont like mixing types in the return. Fix this.
		return tile


	#  Recursively check surrounding tiles for appropriate tiles to reveal
	# returns the total number of tiles revealed during the flood
	def __flood_reveal(self, x, y):
		tiles_revealed_count = 0
		fillable_tile = self.__inside(x, y)
		if fillable_tile is not False:
			# assign our new revealed tile (BLANK or a valid number)
			self.game_state_board[x][y] = fillable_tile
			tiles_revealed_count += 1

			# 	 if we're still looking at a fillable value,
			# ie a BLANK, then we can continue filling here
			if fillable_tile == BLANK:
				# south, north, west, east
				tiles_revealed_count += self.__flood_reveal(x+1, y)
				tiles_revealed_count += self.__flood_reveal(x-1, y)
				tiles_revealed_count += self.__flood_reveal(x, y-1)
				tiles_revealed_count += self.__flood_reveal(x, y+1)

		return tiles_revealed_count

	# reveals all mines in the game state to the player
	def __reveal_mines(self):
		for i, row in enumerate(self.solution_board):
			for j, tile in enumerate(row):
				if tile == MINE:
					self.game_state_board[i][j] = MINE


	def reveal_tile(self):
		if self.solution_board[self.player.x][self.player.y] == MINE:
			self.game_message="YOU DIED LIKE A BITCH."
			self.__reveal_mines()
			self.player_lost = True

		# flood fill traversal
		# TODO: recursive traversal is ineffecient.
		# re-implement with a better flood fill
		x = self.player.x
		y = self.player.y

		self.num_revealed_tiles += self.__flood_reveal(x, y)

		#  game winning condition is if the player successfully has revealed
		# every non-bomb tile
		if self.num_revealed_tiles == self.__total_revealable_tiles():
			self.player_won = True

	def flag_tile(self):
		# first, check if player is recovering a flag
		# TODO: change relationship between player and boards. Add some sort
		# of player.get_current_tile(game_state_board) method 
		if self.game_state_board[self.player.x][self.player.y] == FLAG:
			self.num_flags_remaining += 1
			self.game_state_board[self.player.x][self.player.y] = UNKNOWN
		#  otherwise, they'll be trying to consume a flag. Only allow this if this tile 
		# is flaggable (ie tile is UNKNOWN)
		elif self.game_state_board[self.player.x][self.player.y] == UNKNOWN:
			if self.num_flags_remaining > 0:
				self.game_state_board[self.player.x][self.player.y] = FLAG
				self.num_flags_remaining -= 1
			elif self.num_flags_remaining == 0:
				self.game_message = "NO FLAGS REMAIN"
			else:
				logging.info("impossible flagging case? ({}, {})".format(self.player.x, self.player.y))


if __name__ == '__main__':
	if os.name == 'nt':
		os.system('color')

	parser = argparse.ArgumentParser(description='minesweeper - accepts size and num mines as args')
	parser.add_argument('-s', '--size', type=int, help='A number to set the size of the gameboard', default=10)
	parser.add_argument('-m', '--mines', type=int, help='A number to set the number of mines in the game', default=5)

	args = parser.parse_args()

	if args.mines > (args.size * args.size):
		print("too mane mines for gameboard size")
		exit(5)

	logging.basicConfig(filename="mine.log", level=logging.INFO)
	logging.info(" ")
	logging.info("started minesweeper")

	game = Game(args.size, args.mines)
	DIRECTION_MAP = {d.value:d for d in Direction}

	while game.game_running:
		game.render()
		player_input = input("--> ")
		#  check for player menu options
		if player_input == 'q':
			game.exit()
		#  n is new game
		elif player_input == 'n':
			game = Game(args.size, args.mines)
		#  if player hasn't lost, accept gameplay input
		# other than only menu options
		elif not game.player_lost:
			if player_input in DIRECTION_MAP:
				game.move_player(DIRECTION_MAP[player_input])
			if player_input == 'r':
				game.enable_debug_render()
			if player_input == 'f':
				game.flag_tile()
			if player_input == '':
				game.reveal_tile()

	logging.info("finished minesweeper")
	logging.info(" ")
