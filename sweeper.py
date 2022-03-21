import logging
import random



def print_board(board):
	GRID = (len(board),len(board[0]))

	print(" ", end="")
	for i in range(GRID[0]):
		print("--", end="")
	print()
	
	for i in board:
		print("|",end="")
		for j in i:
			print("{} ".format(j),end="")
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

logging.basicConfig(filename="mine.log", level=logging.INFO)
logging.info(" ")
logging.info("started minesweeper")

MINES = 10
GRID = (10,10)

board = [[" " for x in range(GRID[0])] for i in range(GRID[1])]

print_board(board)

generate_mines(board, MINES)

print_board(board)

logging.info("finished minesweeper")
logging.info(" ")
