from pathlib import Path
import json

currentPath = Path.cwd()
pointsPath = currentPath / "scrabble_points.json"
pointsData = json.load(open(pointsPath))


defaultFiller = '|'
arr = [[defaultFiller for _ in range(15)] for _ in range(15)]

class Scrabble:

	def __init__(self, players, arr) -> None:
		self.players: list[int] = players
		self.gameTurn = 0
		self.game = arr
		pass


	def add_player(self, userID: int):
		self.players.append(userID)

	def next_turn(self):
		if self.gameTurn < len(self.players):
			self.gameTurn += 1
		else:
			self.gameTurn = 0

	def get_surrounding_tiles(self, x: int, y: int):
		tiles = []
		if x > 0:
			if self.game[y][x-1] != defaultFiller:
				tiles.append([y,x-1])
		if x < 14:
			if self.game[y][x+1] != defaultFiller:
				tiles.append([y,x+1])
		if y > 0:
			if self.game[y-1][x] != defaultFiller:
				tiles.append([y-1,x])
		if y < 14:
			if self.game[y+1][x] != defaultFiller:
				tiles.append([y+1, x])
		return x

	def get_cell(self, x: int, y: int):
		return self.game[y][x]
	
	def test_word(self, word: str, initialPosition: tuple[int, int], direction: str, blanks: list[int]):
		if direction == "down":
			# identify if there are already letters there.
			# if there are letters there, check if the word is valid.
			# if no letters, place the word down on the board.
			if initialPosition[1] + len(word) > 15:
				# this will go off the board.
				print("this will go off the board")
				return
			
			x = initialPosition[0]
			y = initialPosition[1]

			# have to change this to check the entire board before doing anything
			for i in range(len(word)):
				print(f'{x} | {y}')
				if self.get_cell(x, y) == defaultFiller:
					# cant replace a cell.
					pass
				else:
					self.game[y][x] = word[i]
					y+=1
			pass

		elif direction == "right":
			pass
		else:
			# This is not allowed, we will not accept this.
			return
	
	def calculate_points(self, word: str, blanks: list[int]):
		# THIS FUNCTION DOES NOT CONSIDER DOUBLE WORDS / LETTERS ETC.
		# blanks are indexes of the word
		points = 0
		for ind in range(len(word)):
			if ind not in blanks:
				points += pointsData[word[ind].upper()]
		return points

	def print_board(self):
		for x in self.game:
			for i in x:
				print(i, end=" ")
			print()


scrab = Scrabble([0, 1], arr)

scrab.test_word("hello", (1,4), "down", [])
scrab.test_word("i", (2,4), "down", [])
print(scrab.calculate_points("hello", []))
scrab.print_board()
