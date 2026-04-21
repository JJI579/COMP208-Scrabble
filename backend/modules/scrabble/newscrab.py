# Plan
# 

from exceptions import *
from typing import Literal, Optional
from pathlib import Path
import json
from enum import Enum
"""
Scrabble class

It will Handle
- Board
- Rules
- Scoring

- Problems
- Lots of side effects per module
- Inconsistent Handling of Data.
"""
# Constants
BOARD_SIZE = 15
BOT_ID = -2
CENTER = (7,7)
EMPTY_TILE = "|"
POINTS_PATH = Path.cwd() / "scrabble_points.json"
POINTS_DATA = json.load(open(POINTS_PATH))
LETTER_BAG_PATH = Path.cwd() / "letter_distribution.json"


# Types
class ModifierValue(Enum):
	DOUBLE_LETTER = "DL"
	TRIPLE_LETTER = "TL"
	DOUBLE_WORD = "DW"
	TRIPLE_WORD = "TW"

class DirectionValue(Enum):
	RIGHT = "RIGHT"
	DOWN = "DOWN"

class Group:
	players: list
	leader: list

class Coordinate:
	x: int
	y: int

	def __init__(self, x: int, y: int) -> None:
		self.x = x
		self.y = y

	def __str__(self) -> str:
		return f"({self.x}, {self.y})"

	def __repr__(self) -> str:
		return f"Coordinate(x={self.x}, y={self.y})"
	
	def export(self):
		return (self.x, self.y)
	
	def is_center(self) -> bool:
		return self.x == CENTER[0] and self.y == CENTER[1]
	
class Letter:
	letter: str
	isBlank: bool = False

	def __init__(self, letter: str, isBlank: bool) -> None:
		self.letter = letter.lower()
		self.isBlank = isBlank

	def __repr__(self) -> str:
		return f"Letter(letter=\"{self.letter}\", isBlank={self.isBlank})"
	
class LetterPlace:
	coordinate: Coordinate
	letter: Letter

	def __init__(self, coordinate: Coordinate, letter: Letter) -> None:
		self.coordinate = coordinate
		self.letter = letter
	
	def __repr__(self) -> str:
		return f"LetterPlace(coordinate={self.coordinate}, letter={self.letter})"

class Turn:
	letters: list[LetterPlace]
	direction: DirectionValue

	def __init__(self, letters: list[LetterPlace], direction: DirectionValue) -> None:
		self.letters = letters
		self.direction = direction


	def __repr__(self) -> str:
		return f"Turn(letters={self.letters}, direction={self.direction})"
class Modifier: 
	modifier: ModifierValue | None
	modifierUsed: bool = False

	def __init__(self, modifier: Optional[ModifierValue] , modifierUsed: bool) -> None:
		self.modifier = modifier
		self.modifierUsed = modifierUsed

class Tile:
	letter: Letter
	modifier: Modifier
	coordinate: Coordinate

	def __init__(self, letter: Letter, modifier: Modifier, coordinate: Coordinate) -> None:
		self.letter = letter
		self.modifier = modifier
		self.coordinate = coordinate


	def update_letter(self, letter: Letter):
		self.letter = letter

	def __str__(self) -> str:
		return f"Tile(letter=\"{self.letter}\")"

	def __repr__(self) -> str:
		return self.__str__()

class Scrabble:

	def __init__(self) -> None:
		# Places of potential extra points.
		self.double_letter = { (3,0),(11,0), (6,2),(8,2), (0,3),(7,3),(14,3), (2,6),(6,6),(8,6),(12,6), (3,7),(11,7), (2,8),(6,8),(8,8),(12,8), (0,11),(7,11),(14,11), (6,12),(8,12), (3,14),(11,14) }
		self.triple_letter = { (5,1),(9,1), (1,5),(5,5),(9,5),(13,5), (1,9),(5,9),(9,9),(13,9), (5,13),(9,13) }
		self.double_word = { (1,1),(2,2),(3,3),(4,4), (7,7), (10,10),(11,11),(12,12),(13,13), (13,1),(12,2),(11,3),(10,4), (4,10),(3,11),(2,12),(1,13) }
		self.triple_word = { (0,0),(7,0),(14,0), (0,7),(14,7), (0,14),(7,14),(14,14) }

		self.grid: list[list[Tile]] = []
		self.placed: list[Tile] = []
		self.finished: bool = False
		self.letterBag = json.load(open(LETTER_BAG_PATH))
		# Used to detect whether the first word has been placed.
		self.placedFirst = False
		
		for y in range(BOARD_SIZE):
			self.grid.append([])
			for x in range(BOARD_SIZE):

				coord = Coordinate(x,y)
				modifier: Modifier = self.calculate_modifier(coord)
				letter = Letter(letter=EMPTY_TILE, isBlank=False)
				tile = Tile(letter=letter, modifier=modifier, coordinate=coord)
				self.grid[y].append(tile)

	def calculate_modifier(self, coordinate: Coordinate) -> Modifier:
		coord = coordinate.export()
		if coord in self.double_letter:
			return Modifier(ModifierValue.DOUBLE_LETTER, False)
		elif coord in self.triple_letter:
			return Modifier(ModifierValue.TRIPLE_LETTER, False)
		elif coord in self.double_word:
			return Modifier(ModifierValue.DOUBLE_WORD, False)
		elif coord in self.triple_word:
			return Modifier(ModifierValue.TRIPLE_WORD, False)
		else:
			return Modifier(None, False)

	# Validation Methods
	def reset_cell(self, coordinate: Coordinate):
		self.grid[coordinate.y][coordinate.x].letter = Letter(letter=EMPTY_TILE, isBlank=False)

	def get_cell(self, coordinate: Coordinate) -> Tile:
		x,y = coordinate.x, coordinate.y
		return self.grid[y][x]

	def is_cell_free(self, Coordinate: Coordinate) -> bool:
		x,y = Coordinate.x, Coordinate.y
		
		return self.grid[y][x].letter.letter == EMPTY_TILE

	def is_word(self, word: str) -> bool:
		word = word.lower()
		if word == "eo":
			return False
		# TODO: validate word
		return True
	
	# Conversion Methods
	def convert_id_to_coordinate(self, squareID: int):
		x = squareID % 15
		y = squareID // 15
		return Coordinate(x, y)

	def convert_coordinate_to_id(self, coordinate: Coordinate):
		x = coordinate.x
		y = coordinate.y
		return (y * 15) + x

	# Word Methods
	def place_letter(self, toPlace: LetterPlace):
		x,y = toPlace.coordinate.x, toPlace.coordinate.y
		
		# this is Tile
		if self.is_cell_free(toPlace.coordinate):
			self.grid[y][x].letter = toPlace.letter
		else:
			raise CellOccupiedError()
	


	# Expansion Methods
	def _collect_contiguous_word(self, position: Coordinate,  direction: DirectionValue) -> list[Coordinate] :
		"""Return the full contiguous word coordinates passing through a board position."""
		x, y = position.export()
		dx, dy = (1, 0) if direction == DirectionValue.RIGHT else (0, 1)

		while 0 <= x - dx < 15 and 0 <= y - dy < 15 and self.get_cell(Coordinate(x - dx, y - dy)).letter.letter != EMPTY_TILE:
			x -= dx
			y -= dy

		coordinates = []
		while 0 <= x < 15 and 0 <= y < 15 and self.get_cell(Coordinate(x, y)).letter.letter != EMPTY_TILE:
			coordinates.append(Coordinate(x,y))
			x += dx
			y += dy

		return coordinates
	
	def expand_vertically(self, position: Coordinate) -> list[Coordinate]:
		return self._collect_contiguous_word(position, DirectionValue.DOWN)
	
	def expand_horizontally(self, position: Coordinate) -> list[Coordinate]:
		return self._collect_contiguous_word(position, DirectionValue.RIGHT)

	

	def can_place_word_here(self, turn: Turn):
		
		
		
		pass


	def simulate_place_word(self, turn: Turn):
		# Simulates whether the word can be placed
		pass

	def valid_first_word_placement(self, turn: Turn):
		hasCenter = False
		for letterPlacement in turn.letters:
			if letterPlacement.coordinate.is_center():
				hasCenter = True
				break
		return hasCenter
	
	def place_word(self, turn: Turn):

		# This is to calculate points for placing the new letters.
		newWords: list[list[Tile]] = []
		newlyPlaced: list[Coordinate] = []

		isWord = False

		# If the first hasn't been placed, check if it a valid first word placement.
		if not self.placedFirst:
			if not self.valid_first_word_placement(turn):
				raise InvalidFirstWordPlacementError()
			else:
				# assume the word that they are to place is the first word and therefore should be correct
				if turn.direction == DirectionValue.DOWN:
					turn.letters.sort(key=lambda letterPlace: letterPlace.coordinate.y)
				else:
					turn.letters.sort(key=lambda letterPlace: letterPlace.coordinate.x)
				isWord = self.is_word(''.join([letterPlace.letter.letter for letterPlace in turn.letters]))


		# Placed all letters
		for letterPlacement in turn.letters:
			if self.is_cell_free(letterPlacement.coordinate):
				# place the word
				self.get_cell(letterPlacement.coordinate).update_letter(letterPlacement.letter)
				newlyPlaced.append(letterPlacement.coordinate)
			else:
				for placed in newlyPlaced:
					self.reset_cell(placed)
				raise CellOccupiedError()
		
		# TODO: Check if board is valid.
		forceBreak = False
		haveTested: list[list[Tile]] = []

		
		hasJoiningWord = False
		# If the word is wrong but we have changed the first placed, then we can reset it via this boolean
		hasSetFirstPlaced = False
		
		for coordinate in newlyPlaced:
			if forceBreak:
				break
			for testDirection in ['right', 'down']:
				if testDirection == "right":
					potentialWord = self.expand_horizontally(coordinate)
				else:
					potentialWord = self.expand_vertically(coordinate)
				testArray = potentialWord.copy()

				# Convert to comparable format and remove already checked

				testArrayConverted = [x.export() for x in testArray]
				for coord in newlyPlaced:
					if coord.export() in testArrayConverted:
						testArrayConverted.remove(coord.export())
				
				# Reconvert back to a list of coordinates
				testArray = [Coordinate(x=coord[0], y=coord[1]) for coord in testArrayConverted]

				if len(testArray) != 0:
					if testDirection == "down":
						potentialWord.sort(key=lambda coord: coord.y )
					else:
						potentialWord.sort(key=lambda coord: coord.x )
					
					wordOrdered: list[Tile] = [self.get_cell(coord) for coord in potentialWord]
					wordString = "".join([tile.letter.letter for tile in wordOrdered])
					print(wordOrdered)
					
					print(f'Checking word found: ' + wordString)
					
					if not self.is_word(wordString):
						isWord = False
						forceBreak = True
						print(f"{wordString} is not a word. ")
						break
					else:
						if wordOrdered in haveTested:
							print("Already tested this word, skipping.")
						else:
							print(f"{wordString} is a word.")
							self.calculate_points([tile.coordinate for tile in wordOrdered])
							hasJoiningWord = True
							isWord = True
							haveTested.append(wordOrdered)
				else:
					if not self.placedFirst:
						hasJoiningWord = True
						self.placedFirst = True
						hasSetFirstPlaced = True

		print(f"hasJoiningWord: {hasJoiningWord}, isWord: {isWord}, hasSetFirstPlaced: {hasSetFirstPlaced}")
		if not hasJoiningWord or not isWord:
			if hasSetFirstPlaced:
				self.placedFirst = False
			# remove coordinates placed
			for coordinate in newlyPlaced:
				self.reset_cell(coordinate)
			raise NoWordsFormedError()
		
		points = 0
		if len(turn.letters) == 7:
			# Full deck
			points += 50

		if points == 0:
			points = self.calculate_turn_points(turn)
		self.placed.extend([self.get_cell(coord) for coord in newlyPlaced])

		# get points for the placement.
		self.print_board()
		return points



	def print_board(self):
		for x in self.grid:
			for i in x:
				print(i.letter.letter, end=" ")
			print()

	
	# Points Method

	def calculate_turn_points(self, turn: Turn):
		coordinates = [letterPlace.coordinate for letterPlace in turn.letters]
		return self.calculate_points(coordinates)
	
	
	def calculate_points(self, coordinates:	list[Coordinate]):
		totalPoints = 0
		wordMultiplierCount = 0
		multiplierType: ModifierValue | None = None
		for coord in coordinates:
			tile = self.get_cell(coord)
			# points for the tile
			points = self.calculate_tile_points(tile)
			# Check if it has a modifier
			if self.tile_has_modifier(tile):
				if tile.modifier.modifier == ModifierValue.DOUBLE_WORD:
					wordMultiplierCount+=1
					multiplierType = ModifierValue.DOUBLE_WORD
				elif tile.modifier.modifier == ModifierValue.TRIPLE_WORD:
					wordMultiplierCount+=1
					multiplierType = ModifierValue.TRIPLE_WORD
				else: 
					if tile.modifier.modifier == ModifierValue.DOUBLE_LETTER:
						points *= 2
					elif tile.modifier.modifier == ModifierValue.TRIPLE_LETTER:
						points *= 3

				# Make the modifier used so it cannot be used again?
				self.set_modifier_used(tile)
			totalPoints += points
		for _ in range(wordMultiplierCount):
			if multiplierType == ModifierValue.DOUBLE_WORD:
				totalPoints *= 2
			elif multiplierType == ModifierValue.TRIPLE_WORD:
				totalPoints *= 3
		return totalPoints
	
	def tile_has_modifier(self, tile: Tile) -> bool:
		return tile.modifier.modifier is not None and not tile.modifier.modifierUsed
	
	def calculate_tile_points(self, tile: Tile) -> int:
		if tile.letter.isBlank:
			return 0
		actualLetter = tile.letter.letter
		return POINTS_DATA.get(actualLetter, 0)

	def set_modifier_used(self, tile: Tile):
		tile.modifier.modifierUsed = True

			