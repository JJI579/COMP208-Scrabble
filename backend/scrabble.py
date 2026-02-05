from pathlib import Path
import json
import requests
import twl

currentPath = Path.cwd()
pointsPath = currentPath / "scrabble_points.json"
pointsData = json.load(open(pointsPath))


defaultFiller = 'x'
arr = [[defaultFiller for _ in range(15)] for _ in range(15)]

# return 
# {
# 	"points": 0,
# 	"word": "",
# 	"placement": [
# 		["id", "letter"]
# 	]
# }
class Scrabble:

	def __init__(self, players, arr) -> None:
		self.players: list[int] = players
		self.gameTurn = 0
		self.game = arr
		self.firstPlaced = False
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
		print(x, y, initialDirection)
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
	

	def expand_vertically(self, position,):
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if y > 0 or y < 16:
				# perform
				if self.game[y][x] != defaultFiller:
					if [x, y] not in coordinates:
						coordinates.append([x, y])
					if traversedBack:
						y+=1
					else:
						y-=1
				else:
					# now go forwards
					if not traversedBack:
						traversedBack = True
						y+=1
					
					else:
						# this shouldve traversed backwards, and now finished going forwards
						break

			else:
				pass

		return coordinates
	
	def expand_horizontally(self, position,):
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if x > 0 or x < 16:
				# perform
				if self.game[y][x] != defaultFiller:
					if [x, y] not in coordinates:
						coordinates.append([x, y])
					if traversedBack:
						x+=1
					else:
						x-=1
				else:
					# now go forwards
					if not traversedBack:
						traversedBack = True
						x+=1
					
					else:
						# this shouldve traversed backwards, and now finished going forwards
						break

			else:
				pass

		return coordinates

	def place_word(self, word: str, position: tuple[int, int], direction: str, blanks: list[int]):
		wordCoordinates = []
		x = position[0]
		y = position[1]
		for i in range(len(word)):
			wordCoordinates.append([x, y])
			if self.get_cell(x, y) != defaultFiller:
				print("cell has already been taken!")
				# TODO: check if there is a word that works otherwise raise an issue.
				return
			else:
				# make it place already to imply that it can be used!
				self.game[y][x] = word[i]
			if direction=="down":
				y+=1
			else:
				x+=1
		
		potentialWord = self.expand_vertically(position)
		if direction == "down":
			potentialWord.sort(key=lambda x: x[1] )
		else:
			potentialWord.sort(key=lambda x: x[0] )
		wordOrdered = [[x, self.get_cell(x[0], x[1])] for x in potentialWord]
		print(wordOrdered)
		# for l in wordOrdered:
		# 	print(l)

		# have to prove that it is connecting some kind of word to make it work.


	def expand_search(self, position: tuple[int, int]):
		# suggest that the word they are placing are considered in the grid.

		# expand up down
		# expand left right
		pass

		

	def test_word(self, word: str, initialPosition: tuple[int, int], direction: str, blanks: list[int]):
		
		if not self.firstPlaced:
			if initialPosition != (7,7):
				print("This is not right position")
				return 
		def formword(sTiles: list, x: int, y: int, i: int):
			wordCreated = ""
			for tile in sTiles:
				if tile == initialPosition:
					# replace with their letter
					wordCreated += word[i]
				else:
					wordCreated+=self.get_cell(*tile)
			return wordCreated
		
		def formMultiLetterWord(sTiles: list, correspondingLetters: list):
			# 2d array of tiles where [[x,y], "a"] coordinate first element, letter second element
			wordCreated = ""
			coordinates = [x[0] for x in correspondingLetters]
			
			for tile in sTiles:
				# stiles = surrounding tiles
				if tile in coordinates:
					wordCreated += [x for x in correspondingLetters if x[0] == tile][0][1]
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
			if considerX and considerY and self.check_word(formedvWord) and self.check_word(formedhWord):
				if blanks:
					points += self.calculate_points(formedhWord, [hWord.index(initialPosition)])
					points += self.calculate_points(formedvWord, [vWord.index(initialPosition)])
				else:
					points += self.calculate_points(formedhWord, [])
					points += self.calculate_points(formedvWord, [])
				pass
			elif considerX and self.check_word(formedhWord):
				if blanks:
					points += self.calculate_points(formedhWord, [hWord.index(initialPosition)])
				else:
					points += self.calculate_points(formedhWord, [hWord.index(initialPosition)])
				pass
			elif considerY and self.check_word(formedvWord):
				if blanks:
					points += self.calculate_points(formedvWord, [vWord.index(initialPosition)])
				else:
					points += self.calculate_points(formedvWord, [])
			else:
				# word is not valid.
				print("not okay")
				return
			
			self.game[initialPosition[1]][initialPosition[0]] = word
			print("points: " + str(points) )
			return

		if direction != "right" and direction != "down":
			print("wrong direction provided.")
			return

		isValid = True
		x = initialPosition[0]
		y = initialPosition[1]

		wordCoordinates = []
		for i in range(len(word)):
			wordCoordinates.append([[x, y], word[i]])
			if direction == "right":
				y+=1
			else:
				x+=1
		
		checked = []
		hasConnectingWord = False
		for i, (coord, letter) in enumerate(wordCoordinates):
			for dir in ['right', 'down']:
				x = coord[0]
				y = coord[1]
				surroundingTiles = self.get_surrounding_tiles(x, y, dir)
				if dir != direction:
					# append all letters to check.
					surroundingTiles.extend([x[0] for x in wordCoordinates])
				else:
					print("Direction")
					# surroundingTiles.extend([x[0] for x in wordCoordinates])

				# Make it sort the letters correctly
				if dir == "down":
					surroundingTiles.sort(key=lambda x: x[0])
					# print(surroundingTiles)
					# print([self.get_cell(*x) for x in surroundingTiles])
				else:
					surroundingTiles.sort(key=lambda x: x[1])
				
				if len(surroundingTiles) == 1:
					if surroundingTiles[0] == [x, y]:
						checked.append([x, y])
				print(surroundingTiles)
				if surroundingTiles not in checked:
					wordCreated = formMultiLetterWord(surroundingTiles, wordCoordinates)
					checked.append(surroundingTiles)
					print("Word Formed: " + wordCreated)
					if len(surroundingTiles) > 1 and surroundingTiles[0] != [x, y]:
						print(f"Checking {wordCreated}")
						if not self.check_word(wordCreated):
							print("This is not a word.")
							isValid = False
							break
						print("Word is fine")
						hasConnectingWord = True
						break
			if hasConnectingWord:
				break
			
			if direction == "right":
				y+=1
			else:
				x+=1

		if (isValid and hasConnectingWord) or (isValid and not self.firstPlaced):
			if direction == "down":
				placeY = initialPosition[1]
				for letter in word:
					self.game[placeY][initialPosition[0]] = letter
					placeY+=1
			else:
				placeX = initialPosition[0]
				for letter in word:
					self.game[initialPosition[1]][placeX] = letter
					placeX+=1
			if not self.firstPlaced:
				self.firstPlaced = True
		elif isValid:
			print("Is valid placement however no connecting word.")
		else:
			print("Not valid placement.")
	
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
		return twl.check(word)
		# resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
		# respData = resp.json()
		# return not ('title' in respData)
	
scrab = Scrabble([0, 1], arr)

scrab.place_word("bet", (7,7), "down", [])
# scrab.test_word("bet", (7,7), "down", [])
scrab.place_word("ee", (8,7), "right", [])
# scrab.test_word("te", (9,5), "down", [])
# scrab.test_word("tit", (3,4), "down", [])
# scrab.test_word("gap", (2,1), "down", [])
# scrab.test_word("t", (3,4), "down", [])

scrab.print_board()

