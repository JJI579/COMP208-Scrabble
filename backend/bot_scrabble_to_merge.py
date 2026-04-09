from pathlib import Path
import json
import requests
# twl doesn't work/exist for me so gonna make my own prefix trie to not use this
#import twl
from sqlalchemy import text
from modules.database.database import get_session, init_db_sync, init_db
import asyncio
import random



# NOTE: uncomment this when/ if databse gets hooked up
'''
init_db_sync()
asyncio.run(init_db())
'''
currentPath = Path.cwd()
pointsPath = currentPath / "scrabble_points.json"
pointsData = json.load(open(pointsPath))


defaultFiller = '|'
arr = [[defaultFiller for _ in range(15)] for _ in range(15)]

# return 
# {
# 	"points": 0,
# 	"word": "",
# 	"placement": [
# 		["id", "letter"]
# 	]
# }
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
			

# TODO: need to consider blanks for the bot, as well as preExisting letters, 
# however the bot should be able to generate words based on the preExisting letters, 
# and then check if it can make them with the letters it has, and if not, ignore them.

# TODO: need to figure out beteter cross word validation as only partially validated currently

# TODO: need to figure out how to use board multipliers and general score calculation needs doing

# TODO: need some sort of scrabble tile rack refil / player turn implementation

# TODO: better legality checks on words potentially would be useful?

# NOTE: some of these should be implemented in player class so pick ur poison jason

'''

bot class that uses a prefix trie to generate possible words based on board state
uses anchor points for where to place a word to reduce list searching
basic score system
decent move simulation based on difficulty

'''


class Bot(Player):

	def __init__(self, name="Bot", difficulty="medium"):
		super().__init__()
		self.name = name
		self.difficulty = difficulty
		self.settings = {
			"easy": {"top_n": 15, "max_len": 4},
            "medium": {"top_n": 5, "max_len": 6},
            "hard": {"top_n": 1, "max_len": 15},
		}
		self.trie = {}
		self.build_trie()

	def build_trie(self):
		with open("sowpods.txt", "r", encoding="utf-8") as f:
			for line in f:
				word = line.strip().upper()
				node = self.trie
				for char in word:
					node = node.setdefault(char, {})
				node["$"] = True

	def choose_move(self, scrabble: "Scrabble"):
		moves = []
		anchors = self.get_candidate_cells(scrabble)

		for x, y in anchors:
			for direction in ["right", "down"]:
				generated = self.generate_possible_words(scrabble, (x, y), direction)

				for word, preExisting in generated:
					points = scrabble.try_place_word(
						word, 
						(x,y), 
						direction, 
						preExisting=preExisting)
					if isinstance(points, int):
						moves.append((points+len(word)*2, word, (x,y), direction, preExisting))
		if not moves:
			return None
		moves.sort(reverse=True, key=lambda x: x[0])
		top_n = self.settings[self.difficulty]["top_n"]
		return random.choice(moves[:top_n])[1:]


	def get_candidate_cells(self, scrabble: "Scrabble"):
		candidates = set()
		for y in range(15):
			for x in range(15):
				if scrabble.get_cell(x,y) != '|':
					continue
				
				for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
					nx, ny = x + dx, y + dy
					if 0 <= nx < 15 and 0 <= ny < 15:
						if scrabble.get_cell(nx, ny) != '|':
							candidates.add((x,y))
							break
		if not candidates:
			candidates.add((7,7))
		return list(candidates)

	def generate_possible_words(self, scrabble: "Scrabble", position, direction):
		x, y = position
		results = []
		seen = set()
		max_len = self.settings[self.difficulty]["max_len"]

		def backtrack(node, path, rack, px, py, preExisting, used_anchor):
			if len(path) > max_len:
				return
			if "$" in node and used_anchor:
				word = "".join(path)
				key = (word, tuple(preExisting))
				if key not in seen:
					seen.add(key)
					results.append((word, preExisting.copy()))
			if not (0<=px<15 and 0<=py<15):
				return
			cell = scrabble.get_cell(px,py)

			if cell != '|':
				letter = cell.upper()
				if letter in node:
					path.append(letter)
					preExisting.append((px, py))
					if direction == "right":
						backtrack(node[letter], path, rack, px+1, py, preExisting, True)
					else:
						backtrack(node[letter], path, rack, px, py+1, preExisting, True)
					path.pop()
					preExisting.pop()
			else:
				cross_allowed = self.cross_check(scrabble, px, py, direction)
				for i, letter in enumerate(rack):
					letter=letter.upper()
					if letter not in node:
						continue
					if letter not in cross_allowed:
						continue
					new_rack=rack[:i]+rack[i+1:]
					path.append(letter)
					if direction == "right":
						backtrack(node[letter], path, new_rack, px+1, py, preExisting, used_anchor)
					else:
						backtrack(node[letter], path, new_rack, px, py+1, preExisting, used_anchor)
					path.pop()
		backtrack(self.trie, [], self.letters.copy(), x, y, [], False)
		return results
	
	def cross_check(self, scrabble, x, y, direction):
		letters= set()
		for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
			original = scrabble.game[y][x]
			scrabble.game[y][x] = c
			if direction == "right":
				coords = scrabble.expand_vertically((x,y))
			else:
				coords = scrabble.expand_horizontally((x,y))
			if len(coords) <= 1:
				letters.add(c)
			else:
				coords_sorted = sorted(coords, key=lambda t: (t[1], t[0]))
				word= ''.join(scrabble.get_cell(cx, cy) for cx, cy in coords_sorted)
				if scrabble.check_word(word):
					letters.add(c)
			scrabble.game[y][x] = original
		return letters





class Scrabble:

	def __init__(self, players, arr) -> None:
		self.players: dict[str, Player] = {

		}
		self.gameTurn = 0
		self.game = arr
		self.firstPlaced = False
		'''
		once again change this if Database is being used for the dictionary???
		'''
		self.word_set = set()
		with open("sowpods.txt", "r", encoding="utf-8") as f:
			for line in f:
				self.word_set.add(line.strip().upper())
		pass

	def add_player(self, userID: int):
		pass
		# self.players.append(userID)

	def next_turn(self):
		if self.gameTurn < len(self.players):
			self.gameTurn += 1
		else:
			self.gameTurn = 0

	def get_cell(self, x: int, y: int):
		return self.game[y][x]
	
	def handle_placement(self, word: str, playerCode: str, preExisting: list[tuple[int, int]] = [], blanks: list[tuple[int, int]] = []):
		# player code is a string that they will use to verify that it is their turn, unless i use their bearer token / session_id to verify its from them?
		pass
	
	def convert_id_to_coordinate(self, squareID: int):
		x = squareID % 15
		y = squareID // 15
		return (x, y)
	
	def convert_coordinate_to_id(self, coordinate: tuple[int, int]):
		x = coordinate[0]
		y = coordinate[1]
		return (y * 15) + x

	def expand_vertically(self, position,):
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
	
	def expand_horizontally(self, position,):
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

	def place_word(self, word: str, position: tuple[int, int], direction: str, blanks: list[tuple[int, int]] = [], preExisting: list[tuple[int, int]] = []):
		wordCoordinates = []
		x = position[0]
		y = position[1]
		print("NEW ONE")
		tempPlaced = []
		for i in range(len(word)):
			if [x,y] not in preExisting:
				wordCoordinates.append([x, y])
			cellContents = self.get_cell(x, y)
			if cellContents != defaultFiller and (x, y) not in preExisting:
				print(x, y)
				print(self.get_cell(x, y))
				print(preExisting)
				# TODO: check if there is a word that works otherwise raise an issue.
				print("cell has already been taken!")
				for x, y in tempPlaced:
					self.game[y][x] = defaultFiller
				return
			else:
				# make it place already to imply that it can be used!
				if (x, y) not in preExisting:
					print("temp placed letter: ", word[i])
					self.game[y][x] = word[i]
					tempPlaced.append([x, y])
				else:
					if self.get_cell(x,y).upper() == word[i]:
						print("missed letter: ", word[i])
					else:
						print(f"mis interpret of letter in preExisting: ({x},{y}) | Preexisting: {self.get_cell(x,y)} | Assumed to be: {word[i]}")
						for x, y in tempPlaced:
							self.game[y][x] = defaultFiller
						return

			if direction=="down":
				y+=1
			else:
				x+=1
		if not self.firstPlaced:
			# MAKE SURE IT CROSSES THE MIDDLE AS START
			if [7,7] not in wordCoordinates:
				return None
			else:
				if self.check_word(word):
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
		isWord = self.check_word(word)
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
					print(f'Checking word found: ' + wordString)
					if not self.check_word(wordString):
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
		
		if len(word) == 7 and len(preExisting) == 0:
			points+=50 

		print(f'{hasJoiningWord} | {isWord} | {word} | Points: {points}')
		
		if self.firstPlaced:
			if not hasJoiningWord or not isWord: 
				pass
				# remove coordinates placed
				for x, y in tempPlaced:
					self.game[y][x] = defaultFiller
				return None
		# for l in wordOrdered:
		# 	print(l)
		return points
		# have to prove that it is connecting some kind of word to make it work.

	def try_place_word(self, word, position, direction, blanks = [], preExisting = []):
		original_board=[row.copy() for row in self.game]
		original_first=self.firstPlaced
		result = self.place_word(word,position,direction,blanks,preExisting)
		self.game=original_board
		self.firstPlaced=original_first
		return result

		
	def calculate_points(self, wordOrdered: list[list], blanks: list[tuple[int, int]]):
		# THIS FUNCTION DOES NOT CONSIDER DOUBLE WORDS / LETTERS ETC.
		# blanks are coordinates of the letter.
		points = 0
		for tupe, letter in wordOrdered:
			if tupe not in blanks:
				# do not ignore
				points += pointsData[letter.upper()]
		return points

		# points = 0
		# for ind in range(len(word)):
		# 	if ind not in blanks:
		# 		points += pointsData[word[ind].upper()]
		# return points

	def print_board(self):
		for x in self.game:
			for i in x:
				print(i, end=" ")
			print()
	'''
	def check_word(self, word: str):
		return asyncio.run(self._check_word(word))
		# return twl.check(word)
		# resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
		# respData = resp.json()
		# return not ('title' in respData)
	
	async def _check_word(self, word: str):
		async for session in get_session():
			resp = await session.execute(text("SELECT * FROM tblWords WHERE word = :word"), {"word": word})
			result = resp.scalar_one_or_none()
			print(f"Word Found: {result}")
			return result
	'''
	# nothing in database so have to use sowpods txt file?????
	# NOTE: not sure if sowpods is good though it has alot of non words ?????

	def check_word(self, word: str):
		return word.upper() in self.word_set
	
	def _check_word_sync(self, word: str):
		word = word.upper()
		with open("sowpods.txt", "r", encoding="utf-8") as f:
			for line in f:
				if line.strip().upper() == word:
					return True
		return False

# test block
if __name__ == "__main__":
	scrab = Scrabble([0, 1], arr)
	'''
	scrab.place_word("protege", (7,4), "down")
	scrab.place_word("epitaxes", (6,4), "right", preExisting=[(7,4)])
	scrab.place_word("taxes", (9,4), "down", preExisting=[(9,4)])
	# scrab.place_word("lazed", (10,3), "right", )
	# scrab.place_word("bet", (7,7), "down", [])
	# scrab.place_word("ee", (8,7), "right", [])
	scrab.place_word("best", (13,2), "down", preExisting=[(13, 4)])
	scrab.place_word("b", (12,3), "down")
	# scrab.place_word("e", (14,2), "right")
	print("\ncheck words\n")
	scrab.check_word("PROTEGE")
	scrab.check_word("ASDFGHJK")
	'''
	scrab.place_word("ant", (7,4), "down")
	print("\nboard start\n")
	scrab.print_board()
	bot=Bot(difficulty="hard")
	bot.append_letters(list("GUBENATORIAL"))
	print("\nbot letter: ", bot.letters)
	move = bot.choose_move(scrab)
	print("\nbots move: ", move)
	if move:
		word, position, direction, preExisting = move
		scrab.place_word(word, position, direction, preExisting=preExisting)
	print("\nboard end\n")
	scrab.print_board()
