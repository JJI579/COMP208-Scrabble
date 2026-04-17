from pathlib import Path
import json
from modules.database.database import get_session
from sqlalchemy import text
import copy
from typing import Literal
from modules.schema import GamePlayer, BotPlayer
import random

currentPath = Path.cwd()
pointsPath = currentPath / "scrabble_points.json"
pointsData = json.load(open(pointsPath))

letterDistribution = currentPath / "letter_distribution.json"
distributionArray = json.load(open(letterDistribution))

wordsPath = currentPath / "sowpods.txt"
with open(wordsPath, "r", encoding="utf-8") as f:
	wordSet = set(line.strip().upper() for line in f if line.strip())

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
		return True
	
class Bot(Player):

	def __init__(self, word_set, name="Bot", difficulty="hard"):
		super().__init__()
		self.name = name
		self.difficulty = difficulty
		self.settings = {
			"easy": {"top_n": 15, "max_len": 4},
			"medium": {"top_n": 5, "max_len": 6},
			"hard": {"top_n": 1, "max_len": 45},
		}
		self.word_set = word_set
		self.trie = {}
		self.build_trie()
		

	def build_trie(self):
		self.trie = {}
		for word in self.word_set:
			word = word.strip().upper()
			node = self.trie
			for char in word:
				node = node.setdefault(char, {})
			node["$"] = True

	def is_word(self, word):
		node = self.trie
		for c in word:
			if c not in node:
				return False
			node = node[c]
		return "$" in node

	async def choose_move(self, scrabble: "Scrabble"):
		# OPTIMIZATION: Limit total moves evaluated to prevent combinatorial explosion
		MAX_MOVES_PER_ANCHOR = 5000  # Limit moves per anchor cell
		MAX_TOTAL_MOVES = 5000      # Total moves to evaluate
		
		moves = []
		anchors = self.get_candidate_cells(scrabble)
		
		# OPTIMIZATION: Sort anchors by potential score (near premium squares)
		anchors = self._prioritize_anchors(scrabble, anchors)
		
		total_moves_evaluated = 0
		
		for anchor_x, anchor_y in anchors:
			if total_moves_evaluated >= MAX_TOTAL_MOVES:
				break
				
			anchor_moves = []
			
			for direction in ["right", "down"]:
				generated = self.generate_possible_words(scrabble, (anchor_x, anchor_y), direction)
				
				for word, pos in generated:
					if total_moves_evaluated >= MAX_TOTAL_MOVES:
						break
						
					word = word.upper()
					if not self.is_word(word):
						continue
						
					points = await scrabble.simulate_place_word(word, pos, direction)
					
					if isinstance(points, int):
						anchor_moves.append((points, word, pos, direction))
						total_moves_evaluated += 1
						
						# Early exit if we have enough good moves from this anchor
						if len(anchor_moves) >= MAX_MOVES_PER_ANCHOR:
							break
							
				if len(anchor_moves) >= MAX_MOVES_PER_ANCHOR:
					break
			
			moves.extend(anchor_moves)
		
		if not moves:
			return None
			
		# Sort by score (already mostly sorted, but ensure it)
		moves.sort(reverse=True, key=lambda x: x[0])
		
		# OPTIMIZATION: Only consider top moves to reduce randomness impact
		top_n = min(self.settings[self.difficulty]["top_n"], len(moves))
		print(f"Found {len(moves)} possible moves, considering top {top_n}")

		chosen_word = random.choice(moves[:top_n])
		points, word, pos, direction = chosen_word
		return chosen_word

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
	
	def _prioritize_anchors(self, scrabble: "Scrabble", anchors):
		"""Sort anchors by potential score (near premium squares, center, etc.)"""
		def anchor_score(anchor):
			x, y = anchor
			score = 0
			
			# Prefer center area
			center_dist = abs(x - 7) + abs(y - 7)
			score -= center_dist * 2  # Closer to center = higher priority
			
			# Prefer positions near premium squares
			for dx in [-1, 0, 1]:
				for dy in [-1, 0, 1]:
					nx, ny = x + dx, y + dy
					if 0 <= nx < 15 and 0 <= ny < 15:
						if (nx, ny) in scrabble.double_word or (nx, ny) in scrabble.triple_word:
							score += 10
						elif (nx, ny) in scrabble.double_letter or (nx, ny) in scrabble.triple_letter:
							score += 5
			
			return score
		
		return sorted(anchors, key=anchor_score, reverse=True)
	
	def cross_check(self, scrabble, x, y, direction):
		"""OPTIMIZATION: Use trie to limit possible letters instead of trying all 26"""
		letters = set()
		
		# When placing horizontally (right), check vertical (down) cross-words
		# When placing vertically (down), check horizontal (right) cross-words
		cross_direction = "down" if direction == "right" else "right"
		
		# Find letters that would form valid cross words
		for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
			if c not in self.letters:
				continue  # Skip letters not in rack
				
			# Temporarily place the letter
			original = scrabble.game[y][x]
			scrabble.game[y][x] = c
			
			try:
				# Check the perpendicular direction for cross-words
				if cross_direction == "right":
					coords = scrabble.expand_horizontally((x, y))
				else:
					coords = scrabble.expand_vertically((x, y))
					
				# If only this single tile, no cross-word formed - letter is valid
				if len(coords) == 1:
					letters.add(c)
				else:
					# Check if the formed cross-word is valid
					coords_sorted = sorted(coords, key=lambda t: (t[1], t[0]) if cross_direction == "right" else (t[0], t[1]))
					word = ''.join(scrabble.get_cell(cx, cy) for cx, cy in coords_sorted)
					if len(word) >= 2 and word.upper() in wordSet:
						letters.add(c)
			finally:
				# Always restore the original state
				scrabble.game[y][x] = original
		
		return letters

	def generate_possible_words(self, scrabble, position, direction):
		x, y = position
		results = []
		seen = set()
		max_len = self.settings[self.difficulty]["max_len"]

		start_x, start_y = x, y

		# rewind to true start of empty segment
		while True:
			prev_x = start_x - 1 if direction == "right" else start_x
			prev_y = start_y - 1 if direction == "down" else start_y

			if not (0 <= prev_x < 15 and 0 <= prev_y < 15):
				break

			if scrabble.get_cell(prev_x, prev_y) != '|':
				start_x, start_y = prev_x, prev_y
			else:
				break

		def backtrack(node, path, rack, px, py, anchor_used, origin):
			if len(path) > max_len:
				return

			if "$" in node and anchor_used:
				word = "".join(path)
				if word not in seen:
					seen.add(word)
					results.append((word, origin))
					# OPTIMIZATION: Limit results per anchor to prevent explosion
					if len(results) >= 20:  # Max 20 words per anchor
						return
				return  # OPTIMIZATION: Don't continue after finding a word

			if not (0 <= px < 15 and 0 <= py < 15):
				return

			# OPTIMIZATION: Early pruning - check if we can still form valid words
			if len(rack) == 0 and "$" not in node:
				return

			cell = scrabble.get_cell(px, py)

			if cell != '|':
				# Existing tile
				letter = cell.upper()
				if letter in node:
					path.append(letter)
					if direction == "right":
						backtrack(node[letter], path, rack, px + 1, py, True, origin)
					else:
						backtrack(node[letter], path, rack, px, py + 1, True, origin)
					path.pop()
			else:
				# Empty tile - try letters from rack
				cross_allowed = self.cross_check(scrabble, px, py, direction)
				
				# OPTIMIZATION: Limit to letters we actually have
				rack_letters = set(rack)
				cross_allowed = cross_allowed & rack_letters
				
				for letter in sorted(cross_allowed):  # Sort for consistency
					if letter not in node:
						continue
						
					rack.remove(letter)  # Temporarily remove from rack
					path.append(letter)

					if direction == "right":
						backtrack(node[letter], path, rack, px + 1, py, True, origin)
					else:
						backtrack(node[letter], path, rack, px, py + 1, True, origin)

					path.pop()
					rack.append(letter)  # Restore to rack

		backtrack(self.trie, [], self.letters.copy(), x, y, False, (start_x, start_y))
		return results
	








class Scrabble:

	def __init__(self, arr) -> None:
		self.players: list[int] = []
		
		self.playerLetters = {
			"player_id": ["letters"]
		}

		self.bot_pass_streak = 0

		# index of array
		self.gameTurn = 0
		self.game = copy.deepcopy(arr)
		# [[x, y], "letter", "blank replacement"]
		self.placed = []  # [(x, y), letter, "blank replacement"]
		self.firstPlaced = False
		# make sure it isnt a reference array
		self.letterArray: list[str] = copy.deepcopy(distributionArray)

		# even though start and finish is in separate places, i am not arsed to fix this.
		self.finished = False

		self.double_letter = [ [3,0],[11,0], [6,2],[8,2], [0,3],[7,3],[14,3], [2,6],[6,6],[8,6],[12,6], [3,7],[11,7], [2,8],[6,8],[8,8],[12,8], [0,11],[7,11],[14,11], [6,12],[8,12], [3,14],[11,14] ]
		self.triple_letter = [ [5,1],[9,1], [1,5],[5,5],[9,5],[13,5], [1,9],[5,9],[9,9],[13,9], [5,13],[9,13] ]
		self.double_word = [ [1,1],[2,2],[3,3],[4,4], [7,7], [10,10],[11,11],[12,12],[13,13], [13,1],[12,2],[11,3],[10,4], [4,10],[3,11],[2,12],[1,13] ]
		self.triple_word = [ [0,0],[7,0],[14,0], [0,7],[14,7], [0,14],[7,14],[14,14] ]

	def export_grid(self):
		toSend = {}
		for (x,y), letter, blankSubstitute in self.placed:
			toSend[str((y*15)+x)] = letter if blankSubstitute == None else blankSubstitute
		return toSend
	
	def fetch_player_letters(self, userID: int):
		# IF GROUP IS TRUE, FETCH LETTERS OF THE PARTNER'S DECK
		
		"""
			Fetches the letters of a given player.

			Args:
				userID (int): The ID of the player whose letters are to be fetched.

			Returns:
				list[str]: The letters of the player.
		"""
		return self.playerLetters[str(userID)]
	
	def fetch_turn(self):
		"""
			Fetches the ID of the player whose turn it is.

			If the game turn is greater than or equal to the number of players,
			return -1, indicating that the game is over.

			Otherwise, return the ID of the player whose turn it is.
		"""
		if self.gameTurn >= len(self.players):
			return -1
		return self.players[self.gameTurn]
	
	def init_game(self, players: list[GamePlayer | BotPlayer]):
		"""
			Initializes the game state with a given list of players.

			Each player is given 7 letters from the letter distribution array.
			The game turn is set to 0, and the function returns the
			userID of the current turn.
		"""

		
		for player in players:
			userID = int(player.userID)
			if userID == -2:
				# they are a bot
				# initialise the bot?
				self.bot = Bot(word_set=wordSet, name="Bot", difficulty="hard")
				self.players.append(-2)
			else:
				self.players.append(userID)
			self.give_player_letters(userID, 7) # base amount in a deck
		# first index of array
		self.gameTurn = 0
		# return userid of first index of array
		return self.players[0] 

	
	async def bot_turn(self) -> int | bool:
		self.bot.letters = self.fetch_player_letters(-2)
		self.bot_pass_streak = 1
		MAX_PASSES = 3
		move = None
		for _ in range(5):  # retry up to 5 times
			move = await self.bot.choose_move(self)
		if not move:
			print("PASS (no valid moves)")
			self.bot_pass_streak += 1
			if self.bot_pass_streak >= MAX_PASSES:
				print("\nStopping: too many passes")
				return False
			return True
		else:
			self.bot_pass_streak = 0

			points, word, pos, direction = move # type: ignore
			print(f"PLAY: {word} at {pos} {direction}")

			try:
				result = await self._place_word(word, pos, direction)
			except Exception as e:
				print("ERROR:", e)
				result = False
			if result:
				temp_letters = self.bot.letters.copy()
				for c in word:
					if c in temp_letters:
						temp_letters.remove(c)
					elif " " in temp_letters:
						temp_letters.remove(" ")
				self.set_player_letters(-2, temp_letters)

				# -2 is bot id; refill the bot rack after play.
				self.give_player_letters(-2, max(0, 7 - len(self.fetch_player_letters(-2))))
				self.bot.letters = self.fetch_player_letters(-2)
				return result
			else:
				print("BOT: place word failed.")
				return False

	def give_player_letters(self, userID: int, amount: int):
		"""
		Gives a player the specified amount of letters.
		If the player already has letters, the new letters will be added to their existing letters.
		Otherwise, the new letters will be stored as the player's letters.
		The letters given will then be removed from the letter array.

		Parameters:
			userID (int): The user ID of the player to give the letters to.
			amount (int): The amount of letters to give to the player.

		Returns:
			None
		"""
		if amount <= 0:
			return
		if len(self.letterArray) == 0:
			if str(userID) in self.playerLetters and len(self.playerLetters[str(userID)]) == 0:
				self.finished = True
				return
			else:
				return

		letterChoices = random.sample(self.letterArray, k=min(amount, len(self.letterArray)))
		if str(userID) not in self.playerLetters:
			self.playerLetters[str(userID)] = []
		self.playerLetters[str(userID)].extend(letterChoices)
		for x in letterChoices:
			try:
				self.letterArray.remove(x)
			except Exception as e:
				print(e)
				print("This will never throw.")

	def set_player_letters(self, userID: int, letters: list[str]):
		""" 
		Set the letters a player has to the given list and then top up their letters to 7 if they have less than 7 letters.

		Parameters:
			userID (int): The user ID of the player to set the letters for.
			letters (list[str]): The list of letters to set the player's letters to.

			Returns:
				None
		"""
		# DONT TRY TO REMOVE FROM THE PARAM SINCE THEY HAVE ALREADY BEEN REMOVED PREVIOUSLY.
		self.playerLetters[str(userID)] = letters
		if len(letters) < 7: # make it give the rest of the letters.
			self.give_player_letters(userID, 7 - len(letters))

	def export_data(self):
		""" 
		Returns a dictionary containing the game state.

		Parameters:
			None

		Returns:
			A dictionary containing the game state with the following keys:
				- "game": The game grid.
				- "players": A list of the user IDs of the players in the game.
				- "gameTurn": The current turn of the game.
		"""
		return {
			"game": self.game,
			"players": self.players,
			"gameTurn": self.gameTurn
		}

	def next_turn(self):
		"""
		Moves the game state to the next player's turn.

		Returns the user ID of the player whose turn it now is.
		"""

		if (self.gameTurn+1) < len(self.players):
			self.gameTurn += 1
		else:
			self.gameTurn = 0
		# Returns user id 
		return self.fetch_turn()

	async def simulate_place_word(self, word: str, position: tuple[int, int], direction: str, blanks: list[tuple[int, int]] = []):
		"""
		Simulates placing a word without modifying the game state.
		Restores the game to its original state after simulation.
		
		Parameters:
			word (str): The word to simulate placing.
			position (tuple[int, int]): The position to place the word.
			direction (str): The direction ('right' or 'down').
			blanks (list[tuple[int, int]]): List of blank tile positions.
			
		Returns:
			int | None: Points earned if valid, None if invalid.
		"""
		snapshot = copy.deepcopy(self.game)
		snapshot_placed = copy.deepcopy(self.placed)
		snapshot_firstPlaced = self.firstPlaced

		result = await self._place_word(word, position, direction, blanks)

		self.game = snapshot
		self.placed = snapshot_placed
		self.firstPlaced = snapshot_firstPlaced

		return result if isinstance(result, int) else None

	def extract_all_words_from_board(self):
		"""Extract all horizontal and vertical words currently on the board"""
		words = []
		
		# Extract horizontal words
		for y in range(15):
			current_word = []
			current_coords = []
			for x in range(15):
				cell = self.get_cell(x, y)
				if cell != defaultFiller:
					current_word.append(cell)
					current_coords.append((x, y))
				else:
					if len(current_word) > 1:
						words.append((''.join(current_word), current_coords[:]))
					current_word = []
					current_coords = []
			if len(current_word) > 1:
				words.append((''.join(current_word), current_coords[:]))
		
		# Extract vertical words
		for x in range(15):
			current_word = []
			current_coords = []
			for y in range(15):
				cell = self.get_cell(x, y)
				if cell != defaultFiller:
					current_word.append(cell)
					current_coords.append((x, y))
				else:
					if len(current_word) > 1:
						words.append((''.join(current_word), current_coords[:]))
					current_word = []
					current_coords = []
			if len(current_word) > 1:
				words.append((''.join(current_word), current_coords[:]))
		
		return words
	
	async def validate_all_board_words(self):
		"""Validate all words currently on the board"""
		words = self.extract_all_words_from_board()
		for word, coords in words:
			if len(word) > 1:  # Only validate multi-letter words
				if not await self.check_word(word):
					return False, word  # Return False and the invalid word
		return True, None

	def get_newly_placed_coords(self, tempPlaced):
		"""Get coordinates of newly placed tiles"""
		return set(coord for coord, _ in tempPlaced)

	def get_cell(self, x: int, y: int):
		""" 
			Returns the value of the cell at the given coordinates (x, y) in the game state.

			Parameters:
				x (int): The x coordinate of the cell to retrieve.
				y (int): The y coordinate of the cell to retrieve.

			Returns:
				The value of the cell at the given coordinates.
		""" 
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
		"""
			Expands vertically from the given position in the game state.

			Returns a list of coordinates (x, y) that the bot can potentially place a word on.

			The expansion starts from the given position and moves upwards until it encounters a cell with the defaultFiller character or the top of the board is reached.

			It then moves downwards until it encounters a cell with the defaultFiller character or the bottom of the board is reached.

			The list of coordinates is returned in the order that they were traversed.

			Parameters:
					position (tuple[int, int]): The position to expand from.

				Returns:
					list[tuple[int, int]]: A list of coordinates (x, y) that the bot can potentially place a word on.
		"""
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if y > 0 and y < 15:
				# perform
				if self.game[y][x] != defaultFiller:
					if (x, y) not in coordinates:
						coordinates.append((x, y))
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
		""" 
			Expands horizontally from the given position in the game state.

			Returns a list of coordinates (x, y) that the bot can potentially place a word on.

			The expansion starts from the given position and moves leftwards until it encounters a cell with the defaultFiller character or the left of the board is reached.

			It then moves rightwards until it encounters a cell with the defaultfiller character or the right of the board is reached.

			The list of coordinates is returned in the order that they were traversed.

			Parameters:
				position (tuple[int, int]): The position to expand from.

			Returns:
				list[tuple[int, int]]: A list of coordinates (x, y) that the bot can potentially place a word on.
		"""
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if x > 0 and x < 15:
				# perform
				if self.game[y][x] != defaultFiller:
					if (x, y) not in coordinates:
						coordinates.append((x, y))
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

	async def place_word(self, letters, direction: str):
		"""
		Places a word on the game board based on the given letters and direction.

		The function takes in a list of coordinates and letters, and a direction string (either "right" or "down").

		It then calculates the coordinates of the word as if it were placed on the board, and calls the _place_word helper function with the calculated coordinates, direction, and blanks.

		Parameters:
			letters (list[tuple[int, int], str]): A list of coordinates and letters, where each coordinate is a tuple of (x, y) and each letter is a string.

			direction (str): A string indicating the direction of the word placement, either "right" or "down".

			blanks (list[tuple[int, int]]): A list of coordinates of blanks on the board.

		Returns:
			int | Literal[False]: The result of the _place_word helper function.

		"""
		print("OUR HELPER FUNCTION --- START --- ")		

		def check_coordinate(coordinate):
			coordinate = [x for x in coordinate]
			for x in self.placed:	
				if x[0] == coordinate:
					return True
			return False

		coords = [x[0] for x in letters]
		for i in range(1, len(coords)):
			x1, y1 = coords[i - 1]
			x2, y2 = coords[i]

			if direction == "right":
				expected = (x1 + 1, y1)
				# Same row, x should increase by exactly 1
				if y1 == y2 and x2 != x1 + 1  and not check_coordinate(expected):
					print(f'right: x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2} | False | expected: {expected}')
					
					return False
			elif direction == "down":
				expected = (x1, y1 + 1)
				
				# Same column, y should increase by exactly 1
				if x1 == x2 and y2 != y1 + 1 and not check_coordinate(expected):
					print(f'down: x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2} | False | expected: {expected}')
					return False

				
		print("OUR HELPER FUNCTION --- END --- ")
		return await self.place_letters(letters)

	async def _place_word(self, word: str, position: tuple[int, int], direction: str, blanks: list[tuple[int, int]] = [], preExisting: list[tuple[int, int]] = []) -> int | Literal[False]:
		"""
		Places a word on the game board based on the given letters and direction.

		The function takes in a list of coordinates and letters, and a direction string (either "right" or "down").

		It then calculates the coordinates of the word as if it were placed on the board, and calls the _place_word helper function with the calculated coordinates, direction, and blanks.

		The function also checks whether the word is a valid English word by calling the check_word function.

		The function returns the number of points that the word is worth, calculated by the calculate_points function.

		Parameters:
			word (str): The word to be placed on the board.

			position (tuple[int, int]): The position to expand from.

			direction (str): A string indicating the direction of the word placement, either "right" or "down".

			blanks (list[tuple[int, int]]): A list of coordinates of blanks on the board.

		Returns:
			int | Literal[False]: The result of the _place_word helper function.

		"""
		
		# Validate word length - must be at least 2 characters
		if len(word) < 2:
			# print(f"INVALID: Word '{word}' is too short (must be 2+ characters)")
			return False
		
		# print(f"Placing word: {word} | Position: {position} | Direction: {direction} | Blanks: {blanks} | PreExisting: {preExisting}") 	
		preExisting = set(preExisting) # type: ignore # consider type of self.placed so this just returns coordinates of previously placed letters
		wordCoordinates = []
		x = position[0]
		y = position[1]
		tempPlaced = []
		direction = direction.lower().strip()
		for i in range(len(word)):
			if (x,y) not in preExisting:
				wordCoordinates.append((x, y))
			cellContents = self.get_cell(x, y)
			if cellContents != defaultFiller:
				if cellContents != word[i]:
					for (x, y), _ in tempPlaced:
						self.game[y][x] = defaultFiller
					return False
			else:
				if (x, y) not in preExisting:
					self.game[y][x] = word[i]
					tempPlaced.append(((x, y), word[i]))
				else:
					if self.get_cell(x,y) == word[i]:
						pass
					else:
						for (x, y), *_ in tempPlaced:
							self.game[y][x] = defaultFiller
						return False

			if direction == "down":
				y+=1
			else:
				x+=1
		if not self.firstPlaced:
			# MAKE SURE IT CROSSES THE MIDDLE AS START
			if (7,7) not in wordCoordinates:
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
		# print(f"word: {word}")
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
				testArray = potentialWord.copy()
				[testArray.remove(x) for x in wordCoordinates if x in testArray]
				if len(testArray) != 0:
					if testDirection == "down":
						potentialWord.sort(key=lambda x: x[1] )
					else:
						potentialWord.sort(key=lambda x: x[0] )
					wordOrdered = [[x, self.get_cell(x[0], x[1])] for x in potentialWord]
					wordString = ''.join([x[1] for x in wordOrdered])
					
					# Validate cross-word is at least 2 characters
					if len(wordString) < 2:
						# print(f"INVALID CROSS-WORD: '{wordString}' is too short")
						for (x, y), _ in tempPlaced:
							self.game[y][x] = defaultFiller
						return False
					
					# print(wordString)
					# print(f'Checking word found: ' + wordString)
					if not await self.check_word(wordString):
						# print(f"INVALID CROSS-WORD: '{wordString}' is not in dictionary")
						for (x, y), _ in tempPlaced:
							self.game[y][x] = defaultFiller
						return False
						# print(f"{wordString} is not a word. ")
						break
					else:
						# print(f"{wordString} is a word.")
						# print(wordOrdered)
						# Only apply modifiers to newly placed tiles in cross-words
						newly_placed_in_cross = [t for t in wordOrdered if tuple(t[0]) in [(c[0], c[1]) for c in wordCoordinates]]
						existing_in_cross = [t for t in wordOrdered if tuple(t[0]) not in [(c[0], c[1]) for c in wordCoordinates]]
						
						# Add points for existing tiles (no modifiers)
						for coord, letter in existing_in_cross:
							if coord not in blanks:
								points += pointsData[letter.upper()]
						
						# Add points for newly placed tiles (with modifiers)
						points += self.calculate_points(newly_placed_in_cross, blanks)
						
						hasJoiningWord = True
						isWord = True
				else:
					if not self.firstPlaced:
						hasJoiningWord = True
						self.firstPlaced = True
		
		if len(word) == 7 and len(preExisting) == 0:
			points+=50 
		points+=self.calculate_points(tempPlaced, blanks)
		
		# STRICT VALIDATION: Always check that main word is valid
		if not isWord:
			# print(f"INVALID MAIN WORD: '{word}' is not in dictionary")
			for (x, y), _ in tempPlaced:
				self.game[y][x] = defaultFiller
			return False
		
		# COMPREHENSIVE VALIDATION: Check all words on the board are valid
		all_valid, invalid_word = await self.validate_all_board_words()
		if not all_valid:
			# print(f"INVALID WORD ON BOARD: '{invalid_word}'")
			for (x, y), _ in tempPlaced:
				self.game[y][x] = defaultFiller
			return False
		
		if self.firstPlaced:
			if not hasJoiningWord: 
				# print("removing placed letters - no joining word")
				# remove coordinates placed
				for (x, y), letter in tempPlaced:
					self.game[y][x] = defaultFiller
				return False
			else:
				pass
		
		for x in tempPlaced:
			coord, letter = x
			self.placed.append([coord, letter, None])
		return points

	async def place_letters(self, letters: list[tuple[tuple[int, int], str, str|None]]):
		

		hasSetFirstPlaced = False
		isWord = False
		if not self.firstPlaced:
			# make sure [8,8] in the letters
			if [7,7] not in [x[0] for x in letters]:
				print("Not first required placement in grid so returning false")
				return False
			
			wordString = ""
			for (x, y), letter, blankSubstitute in letters:
				wordString+=letter if blankSubstitute == None else blankSubstitute
			isWord = await self.check_word(wordString)

		boardLetters = [x[0] for x in self.placed]
		
		placing = []
		blanks = []
		points = 0

		for i, ((x,y), letter, blankSubstitute) in enumerate(letters):
			toPlace = (letter if blankSubstitute == None else blankSubstitute).upper()
			if letter == " ":
				# gather the blank positions
				blanks.append((x,y))

			if (x,y) in boardLetters:
				# reset the board
				for placed_item in placing:
					temp_x, temp_y = placed_item[0]
					self.game[temp_y][temp_x] = defaultFiller
				print("Exited here")
				return False
			else:
				placing.append(letters[i])
				self.game[y][x] = toPlace

		# Now it is all placed onto the grid, so check each letter and verify it has a valid word.
		letterPositions = [x[0] for x in letters]
		forceBreak = False
		hasJoiningWord = False
		
		haveTested = []
		for currentPosition in letterPositions:
			if forceBreak:
				break
			for testDirection in ['right', "down"]:
				if testDirection == "right":
					potentialWord = self.expand_horizontally(currentPosition)
				else:
					potentialWord = self.expand_vertically(currentPosition)
					
				testArray = potentialWord.copy()
				[testArray.remove(x) for x in [(a[0], a[1]) for a in letterPositions] if x in testArray]
				if len(testArray) != 0:
					if testDirection == "down":
						potentialWord.sort(key=lambda x: x[1] )
					else:
						potentialWord.sort(key=lambda x: x[0] )
					wordOrdered = [[x, self.get_cell(x[0], x[1])] for x in potentialWord]
					wordString = ''.join([x[1] for x in wordOrdered])
					print(wordOrdered)
					
					print(f'Checking word found: ' + wordString)
					self.print_board()
					if not await self.check_word(wordString):
						isWord = False
						forceBreak = True
						print(f"{wordString} is not a word. ")
						break
					else:
						if wordOrdered in haveTested:
							print("Already tested this word, skipping.")
						else:
							print(f"{wordString} is a word.")
							points+=self.calculate_points(wordOrdered, blanks)
							hasJoiningWord = True
							isWord = True
							haveTested.append(wordOrdered)
				else:
					if not self.firstPlaced:
						hasJoiningWord = True
						self.firstPlaced = True
						hasSetFirstPlaced = True
		print(f'has join word: {hasJoiningWord} | isword: {isWord} | {letters} | Points: {points}')
		if not hasJoiningWord or not isWord:
			if hasSetFirstPlaced:
				self.firstPlaced = False
			print("removing placed letters")
			# remove coordinates placed
			for (x, y), *_ in placing:
				self.game[y][x] = defaultFiller
			return False
		# OTHERWISE IT IS A TRUE WORD.
		self.placed.extend(placing)
		print("before giving points")
		if points == 0:
			points+=self.calculate_points(placing, blanks)
		print(points)
		return points
	
		

	def calculate_points(self, wordOrdered: list[list], blanks: list[tuple[int, int]]):
		# This function should ONLY be called with newly placed tiles
		doubleWord = 0
		tripleWord = 0
		points = 0
		print(blanks)
		for coord, letter, *rest in wordOrdered:
			
			if coord not in blanks:
				# do not ignore
				if letter != " ":

					if coord in self.double_letter:
						self.double_letter.remove(coord)
						points += (pointsData[letter.upper()]*2) 
					elif coord in self.triple_letter:
						self.triple_letter.remove(coord)
						points += (pointsData[letter.upper()] * 3)
				
				if coord in self.double_word:
					self.double_word.remove(coord)
					doubleWord+=1
				elif coord in self.triple_word:
					self.triple_word.remove(coord)
					tripleWord+=1
				if letter != " ":
					# blanks have no points
					points += pointsData[letter.upper()]
			else:
				# Blank tiles have no points
				pass

		for _ in range(doubleWord):
			points*=2
		for _ in range(tripleWord):
			points*=3
		return points

	def print_board(self):
		for x in self.game:
			for i in x:
				print(i, end=" ")
			print()

	async def check_word(self, word: str) -> bool:
		"""
			Check if a word is present in the database.
			
			Args:
				word (str): The word to check.

			Returns:
				bool: True if the word is present, False otherwise.
		"""
		return word.upper() in wordSet
	""" 	
		async for session in get_session():
			resp = await session.execute(text("SELECT 1 FROM tblWords WHERE word = :word LIMIT 1"), {"word": word.lower()})
			result = resp.scalar_one_or_none()
			print(f"Word Found: {result}")
			return result is not None
		return False """




async def load_word_set():
	words = []
	async for session in get_session():
		result = await session.execute(text("SELECT word FROM tblWords"))
		words = [row[0].upper() for row in result.fetchall()]
	return words

async def create_game():
	word_set = await load_word_set()
	game = Scrabble(arr)
	bot = Bot(word_set, name="Bot", difficulty="hard")
	return game, bot