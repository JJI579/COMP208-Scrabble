from pathlib import Path
import json
import requests
import twl

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

	def get_surrounding_tiles(self, x: int, y: int, initialDirection: str):
		tiles = []

		if initialDirection == "down":
			# return only right and left of the coordinates
			initialX = x
			x-=1
			if self.game[y][x] != defaultFiller:
				while True:
					if x >= 0:
						if self.game[y][x] != defaultFiller:
							if [x, y] not in tiles:
								tiles.append([x, y])
						else:
							break
						x -= 1
					else:
						break
			x = initialX
			x+=1
			if self.game[y][x] != defaultFiller:
				while True:
					if x < 15:
						print(x, y)
						if self.game[y][x] != defaultFiller:
							if [x, y] not in tiles:
								tiles.append([x, y])
						else:
							break
						x += 1
					else:
						break
		else:
			# up and down direction
			initialY = y
			y-=1
			if self.game[y][x] != defaultFiller:
				while True:
					if y >= 0:
						if self.game[y][x] != defaultFiller:
							if [x, y] not in tiles:
								tiles.append([x, y])
						else:
							break
						y -= 1
					else:
						break
			y = initialY
			y+=1
			if self.game[y][x] != defaultFiller:
				while True:
					if y <= 15:
						if self.game[y][x] != defaultFiller:
							if [x, y] not in tiles:
								tiles.append([x, y])
						else:
							break
						y += 1
					else:
						break
		return tiles
		
	def get_cell(self, x: int, y: int):
		return self.game[y][x]
	
	def test_word(self, word: str, initialPosition: tuple[int, int], direction: str, blanks: list[int]):
		
		def formword(sTiles: list, x: int, y: int, i: int):
			wordCreated = ""
			for tile in sTiles:
				if tile == initialPosition:
					# replace with their letter
					wordCreated += word[i]
				else:
					wordCreated+=self.get_cell(*tile)
			return wordCreated
		
		if len(word) == 1:
			# maybe check if it will go off the board?
			# check both directions
			considerX = True
			considerY = True
			vWord = self.get_surrounding_tiles(initialPosition[0], initialPosition[1], "down")
			hWord = self.get_surrounding_tiles(initialPosition[0], initialPosition[1], "right")
			vWord.append(initialPosition)
			if len(hWord) == 0:
				# do not consider
				considerX = False
			elif len(vWord) == 0:
				considerY = False
			hWord.append(initialPosition)
			vWord.sort(key=lambda x: x[0])
			hWord.sort(key=lambda x: x[1])
			formedvWord = formword(vWord, initialPosition[0], initialPosition[1], 0)
			formedhWord = formword(hWord, initialPosition[0], initialPosition[1], 0)
			points = 0
			# if there are blanks, there will be only one blank since... after all there is one letter.
			if considerX and considerY and twl.check(formedvWord) and twl.check(formedhWord):
				if blanks:
					points += self.calculate_points(formedhWord, [hWord.index(initialPosition)])
					points += self.calculate_points(formedvWord, [vWord.index(initialPosition)])
				else:
					points += self.calculate_points(formedhWord, [])
					points += self.calculate_points(formedvWord, [])
				pass
			elif considerX and twl.check(formedhWord):
				if blanks:
					points += self.calculate_points(formedhWord, [hWord.index(initialPosition)])
				else:
					points += self.calculate_points(formedhWord, [hWord.index(initialPosition)])
				pass
			elif considerY and twl.check(formedvWord):
				if blanks:
					points += self.calculate_points(formedvWord, [vWord.index(initialPosition)])
				else:
					points += self.calculate_points(formedvWord, [])
			else:
				# word is not valid.
				print("not okay")
				return
			print("okay!")
			self.game[initialPosition[1]][initialPosition[0]] = word
			print("points: " + str(points) )
			return

		if direction == "down":
			# identify if there are already letters there.
			# if there are letters there, check if the word is valid.
			# if no letters, place the word down on the board.
			
			
			x = initialPosition[0]
			y = initialPosition[1]

			# have to change this to check the entire board before doing anything
			isValid = True
			for i in range(len(word)):
				# print(f'{x} | {y}')
				if self.get_cell(x, y) == defaultFiller:
					# For every letter in the word you are constructing, check if there are any words branching off it.
					surroundingTiles = self.get_surrounding_tiles(x, y, direction)
					surroundingTiles.append([x, y])
					surroundingTiles.sort(key=lambda x: x[0])

					# form the word.
					

					# check if word exists
					wordCreated = formword(surroundingTiles, x, y, i)
					print(wordCreated)
					if len(surroundingTiles) > 1 and surroundingTiles[0] != [x, y]:
						print(f"Checking {wordCreated}")
						if not self.check_word(wordCreated):
							print("This is not a word.")
							isValid = False
							break
						print("Word is fine")
						# calculate the points of the word 
						# have to consider whether itll be double points
					y+=1
					pass
				else:
					# cant replace a cell.
					isValid = False
					pass

			if isValid:
				print("This is valid")
				placeY = initialPosition[1]
				for letter in word:
					self.game[placeY][x] = letter
					placeY+=1
			else:
				print("Not valid placement.")


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

	def check_word(self, word: str):
		resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
		respData = resp.json()
		return not ('title' in respData)
	
scrab = Scrabble([0, 1], arr)

scrab.test_word("bet", (1,4), "down", [])
scrab.test_word("tit", (3,4), "down", [])
scrab.test_word("gap", (2,1), "down", [])
scrab.test_word("e", (2,4), "right", [0])
# scrab.test_word("t", (3,4), "down", [])
scrab.print_board()

