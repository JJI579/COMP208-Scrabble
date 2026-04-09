from pathlib import Path
import json
from backend.modules.database.database import get_session
from sqlalchemy import text
import asyncio
import copy
from typing import Literal
from backend.modules.schema import GamePlayer
import random

currentPath = Path.cwd()
pointsPath = currentPath / "scrabble_points.json"
pointsData = json.load(open(pointsPath))

letterDistribution = currentPath / "letter_distribution.json"
distributionArray = json.load(open(letterDistribution))


defaultFiller = '|'
arr = [[defaultFiller for _ in range(15)] for _ in range(15)]

class Player:

	def __init__(self) -> None:
		self.letters = []

	def append_letters(self, toGive: list[str]):
		for x in toGive:
			self.letters.append(x)

	def remove_letters(self, toTake: list[str]):
		for x in toTake:
			try:
				self.letters.remove(x)
			except ValueError:
				print(f"A letter to be removed is NOT in the players letter category | Letter: {x}")

	def can_make(self, word: str, blanks: list[tuple[int, int]] = [], preExisting: list[tuple[int, int]] = []):
		wordMap = {}
		availableCount = {}
		# TODO: consider preExisting - too late im considering it before you - hari
		for x in word:
			if x not in wordMap:
				wordMap[x] = 1
			else:
				wordMap[x] += 1
			availableCount[x] = self.letters.count(x)
		
		for key, val in wordMap.items():
			if key not in availableCount:
				return False
			if availableCount[key] < val:
				return False
			
# class Bot(Player):

# 	def __init__(self, name="Bot"):
# 		super().__init__()
# 		self.name = name

# 	def choose_move(self, scrabble: "Scrabble"):
# 		best_move = None
# 		best_score = -1
# 		# try to get the cells next to already placed - more efficient that checking every cell xx
# 		candidates = self.get_candidate_cells(scrabble)
# 		for x, y in candidates:
# 			for direction in ["right", "down"]:
# 				for word in self.get_possible_words(scrabble):
# 					preExisting = self.find_matching_letters(scrabble, word, x, y, direction)
# 					# print(f"Testing word: {word} at position: ({x}, {y}) in direction: {direction} with preExisting: {preExisting}")
					
# 					#save board incase we need to revert
# 					temp = [row.copy() for row in scrabble.game]

# 					# coords for calculating points
# 					points = scrabble.draft_place_word(word, (x,y), direction, blanks=[], preExisting=preExisting, draft=True)
# 					if points > best_score:
# 						best_score = points
# 						best_move = (word, (x,y), direction, preExisting)
# 					# restore
# 					scrabble.game = temp
# 		return best_move
# 	# check bots placed tiles...
# 	''' TODO: get candidate cells, get possible words, find matchingn letters
# 				difficulty levels?
# 					-> considers intersecting words and considers tile multipliers..
# 	'''
	
# 	def get_candidate_cells(self, scrabble: "Scrabble"):
# 		pass

# 	def get_possible_words(self, scrabble: "Scrabble"):
# 		possible_words = []
# 		pass

# 	def find_matching_letters(self, scrabble: "Scrabble", word, position, direction):
# 		x, y = position
# 		preExisting = []
# 		pass





class Scrabble:

	def __init__(self, arr) -> None:
		self.players: list[int] = []
		self.playerLetters = {
			"player_id": ["letters"]
		}
		# index of array
		self.gameTurn = 0
		self.game = arr
		# [[x, y], "letter"]
		self.placed = []  # [(x, y), letter]
		self.firstPlaced = False
		# make sure it isnt a reference array
		self.letterArray: list[str] = copy.deepcopy(distributionArray)


		self.double_letter = [ [3,0],[11,0], [6,2],[8,2], [0,3],[7,3],[14,3], [2,6],[6,6],[8,6],[12,6], [3,7],[11,7], [2,8],[6,8],[8,8],[12,8], [0,11],[7,11],[14,11], [6,12],[8,12], [3,14],[11,14] ]
		self.triple_letter = [ [5,1],[9,1], [1,5],[5,5],[9,5],[13,5], [1,9],[5,9],[9,9],[13,9], [5,13],[9,13] ]
		self.double_word = [ [1,1],[2,2],[3,3],[4,4], [7,7], [10,10],[11,11],[12,12],[13,13], [13,1],[12,2],[11,3],[10,4], [4,10],[3,11],[2,12],[1,13] ]
		self.triple_word = [ [0,0],[7,0],[14,0], [0,7],[14,7], [0,14],[7,14],[14,14] ]

	def export_grid(self):
		toSend = {}
		for [x,y], letter in self.placed:
			toSend[str((y*15)+x)] = letter
		return toSend
	
	def fetch_player_letters(self, userID: int):
		return self.playerLetters[str(userID)]
	
	def fetch_turn(self):
		if self.gameTurn >= len(self.players):
			return -1
		return self.players[self.gameTurn]
	
	def init_game(self, players: list[GamePlayer]):
		for player in players:
			userID = int(player.userID)
			self.players.append(userID)
			self.give_player_letters(userID, 7) # base amount in a deck
		self.gameTurn = 0
		# return userid of current turn
		return self.players[0] 

	def give_player_letters(self, userID: int, amount: int):
		letterChoices = random.sample(self.letterArray, k=amount)
		letterChoices[0] = " "
		if str(userID) in self.playerLetters:
			self.playerLetters[str(userID)].extend(letterChoices)
		else:
			self.playerLetters[str(userID)] = letterChoices
		for x in letterChoices:
			print("give player letter")
			print(x)
			try:
				self.letterArray.remove(x)
			except Exception as e:
				print(e)
				print("This will never throw.")

	def set_player_letters(self, userID: int, letters: list[str]):
		# give player rest of letters aswell.
		# DONT TRY TO REMOVE FROM THE PARAM SINCE THEY HAVE ALREADY BEEN REMOVED PREVIOUSLY.
		self.playerLetters[str(userID)] = letters
		if len(letters) < 7: # make it give the rest of the letters.
			self.give_player_letters(userID, 7 - len(letters))

	def export_data(self):
		return {
			"game": self.game,
			"players": self.players,
			"gameTurn": self.gameTurn
		}

	def next_turn(self):
		# TODO: change this to the next player's user id not game turn - i think?	

		if (self.gameTurn+1) < len(self.players):
			self.gameTurn += 1
		else:
			self.gameTurn = 0
		# Returns user id 
		return self.fetch_turn()

	def get_cell(self, x: int, y: int):
		return self.game[y][x]
	
	def convert_id_to_coordinate(self, squareID: int):
		x = squareID % 15
		y = squareID // 15
		return (x, y)
	
	def convert_coordinate_to_id(self, coordinate: tuple[int, int]):
		x = coordinate[0]
		y = coordinate[1]
		return (y * 15) + x

	def expand_vertically(self, position):
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if y > 0 and y < 15:
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
				break

		return coordinates
	
	def expand_horizontally(self, position):
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if x > 0 and x < 15:
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
				break

		return coordinates

	async def place_word(self, letters, direction: str, blanks: list[tuple[int, int]]):

		# letters = list of [[x,y], letter]
		# aim of this is for the game to calculate what word is trying to be made

		# THIS THEN GETS PASSED TO _PLACE_WORD
		
		return await self._place_word(''.join([x[1] for x in letters]), letters[0][0], direction.lower(), blanks=blanks) # type: ignore

	async def _place_word(self, word: str, position: tuple[int, int], direction: str, blanks: list[tuple[int, int]] = [], preExisting: list[tuple[int, int]] = []) -> int | Literal[False]:
		print(f"Placing word: {word} | Position: {position} | Direction: {direction} | Blanks: {blanks} | PreExisting: {preExisting}") 	
		preExisting = [x[0] for x in self.placed] # consider type of self.placed so this just returns coordinates of previously placed letters
		wordCoordinates = []
		x = position[0]
		y = position[1]
		tempPlaced = []
		for i in range(len(word)):
			if [x,y] not in preExisting:
				wordCoordinates.append([x, y])
			cellContents = self.get_cell(x, y)
			if cellContents != defaultFiller and (x, y) not in preExisting:
				# TODO: check if there is a word that works otherwise raise an issue.
				print("cell has already been taken!")
				for [x, y], letter in tempPlaced:
					self.game[y][x] = defaultFiller
				return False
			else:
				# make it place already to imply that it can be used!
				if (x, y) not in preExisting:
					print("temp placed letter: ", word[i])
					self.game[y][x] = word[i]
					tempPlaced.append([[x, y], word[i]])
				else:
					if self.get_cell(x,y) == word[i]:
						print("missed letter: ", word[i])
					else:
						print(f"mis interpret of letter in preExisting: ({x},{y}) | Preexisting: {self.get_cell(x,y)} | Assumed to be: {word[i]}")
						for [x, y], letter in tempPlaced:
							self.game[y][x] = defaultFiller
						return False

			if direction=="down":
				y+=1
			else:
				x+=1
		if not self.firstPlaced:
			# MAKE SURE IT CROSSES THE MIDDLE AS START
			if [7,7] not in wordCoordinates:
				return False
			else:
				if await self.check_word(word):
					# fine
					pass
				# check the word and allow placement.

		# we need to implement below on every letter, however if the direction of the letter is going down, then you only need to consider horizontal for each letter
		# and if the word placed was right, considered up and down along every letter, then see how that goes...
		# NOTE: pretty sure i have got it working...

		# below works for basic concatenation

		# assume there is no joining word till proved
		hasJoiningWord = False
		# assume every connection is a word until proven wrong
		# also we assume that they can provide us either a word, or not, if it is a word, prove wrong via connections, else it is fine.
		print(f"word: {word}")
		isWord = await self.check_word(word)
		forceBreak = False
		points = 0
		for currentPosition in wordCoordinates:
			if forceBreak:
				break
			for testDirection in ['right', "down"]:
				if testDirection == "right":
					potentialWord = self.expand_horizontally(currentPosition)
				else:
					potentialWord = self.expand_vertically(currentPosition)
					print(potentialWord)
				testArray = potentialWord.copy()
				[testArray.remove(x) for x in wordCoordinates if x in testArray]
				if len(testArray) != 0:
					if testDirection == "down":
						potentialWord.sort(key=lambda x: x[1] )
					else:
						potentialWord.sort(key=lambda x: x[0] )
					wordOrdered = [[x, self.get_cell(x[0], x[1])] for x in potentialWord]
					wordString = ''.join([x[1] for x in wordOrdered])
					print(wordString)
					print(f'Checking word found: ' + wordString)
					if not await self.check_word(wordString):
						isWord = False
						forceBreak = True
						print(f"{wordString} is not a word. ")
						break
					else:
						print(f"{wordString} is a word.")
						points+=self.calculate_points(wordOrdered, blanks)
						hasJoiningWord = True
						isWord = True
				else:
					if not self.firstPlaced:
						hasJoiningWord = True
						self.firstPlaced = True
		
		# TODO: fix 50 points issue and make it not consider preExisting.
		if len(word) == 7 and len(preExisting) == 0:
			points+=50 
		# calculate points for the literal word
		# TODO: this will not work for future make this work.
		points+=self.calculate_points(tempPlaced, blanks)

		print(f'{hasJoiningWord} | {isWord} | {word} | Points: {points}')
		
		if self.firstPlaced:
			if not hasJoiningWord or not isWord: 
				print("removing placed letters")
				# remove coordinates placed
				for [x, y], letter in tempPlaced:
					self.game[y][x] = defaultFiller
				return False
			else:
				pass
		
		self.placed.extend(tempPlaced)
		self.print_board()
		return points
		
	def calculate_points(self, wordOrdered: list[list], blanks: list[tuple[int, int]]):
		# TODO: fix blanks.
		doubleWord = 0
		tripleWord = 0
		points = 0
		for coord, letter in wordOrdered:
			if coord not in blanks:
				# do not ignore
				if coord in self.double_letter:
					self.double_letter.remove(coord)
					points += (pointsData[letter.upper()]*2) 
				elif coord in self.triple_letter:
					self.triple_letter.remove(coord)
					points += (pointsData[letter.upper()] * 3)
				else:
					if coord in self.double_word:
						self.double_word.remove(coord)
						doubleWord+=1
					elif coord in self.triple_word:
						self.triple_word.remove(coord)
						tripleWord+=1
					points += pointsData[letter.upper()] 

		for _ in range(doubleWord):
			print("[POINTS] | Doubled word points")
			points*=2
		for _ in range(tripleWord):
			print("[POINTS] | Tripled word points")
			points*=3
		return points

	def print_board(self):
		for x in self.game:
			for i in x:
				print(i, end=" ")
			print()

	async def check_word(self, word: str):
		# return True
		return await self._check_word(word)
	
	async def _check_word(self, word: str):
		async for session in get_session():
			resp = await session.execute(text("SELECT * FROM tblWords WHERE word = :word"), {"word": word.lower()})
			result = resp.scalar_one_or_none()
			print(f"Word Found: {result}")
			return result