import random

MINES = 10
GRID = (10,10)

board = [[" " for x in range(GRID[0])] for i in range(GRID[1])]

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
