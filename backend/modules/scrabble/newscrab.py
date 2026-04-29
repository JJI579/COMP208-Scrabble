# Plan


from exceptions import *
from scrabble_types import *
from pathlib import Path
import json



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

	def copy(self) -> "Scrabble":
		new = Scrabble()

		new.grid = [
			[Tile(
				Letter(tile.letter.letter, tile.letter.isBlank),
				Modifier(tile.modifier.modifier, tile.modifier.modifierUsed),
				Coordinate(tile.coordinate.x, tile.coordinate.y)
			) for tile in row]
			for row in self.grid
		]

		new.placed = self.placed.copy()
		new.placedFirst = self.placedFirst
		new.finished = self.finished

		return new
	
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

	def valid_first_word_placement(self, turn: Turn):
		hasCenter = False
		for letterPlacement in turn.letters:
			if letterPlacement.coordinate.is_center():
				hasCenter = True
				break
		return hasCenter

	def validate_turn(self, turn: Turn) -> ValidationResult:
		# 1. First move must hit center
		if not self.placedFirst:
			if not self.valid_first_word_placement(turn):
				raise InvalidFirstWordPlacementError()

		# 2. Ensure all cells are free
		for lp in turn.letters:
			if not self.is_cell_free(lp.coordinate):
				raise CellOccupiedError()

		# 3. Simulate on a temp board (NO mutation to real board)
		temp = self.copy()

		for lp in turn.letters:
			temp.get_cell(lp.coordinate).update_letter(lp.letter)

		new_coords = [lp.coordinate for lp in turn.letters]

		words = []
		seen = set()

		for coord in new_coords:
			for direction in [DirectionValue.RIGHT, DirectionValue.DOWN]:
				if direction == DirectionValue.RIGHT:
					coords = temp.expand_horizontally(coord)
				else:
					coords = temp.expand_vertically(coord)

				if len(coords) <= 1:
					continue

				coords_sorted = sorted(
					coords,
					key=lambda c: c.x if direction == DirectionValue.RIGHT else c.y
				)

				key = tuple((c.x, c.y) for c in coords_sorted)
				if key in seen:
					continue
				seen.add(key)

				word = "".join(
					temp.get_cell(c).letter.letter for c in coords_sorted
				)

				if not self.is_word(word):
					raise InvalidMainWordError()

				words.append(coords_sorted)

		if not words:
			raise NoWordsFormedError()

		return ValidationResult(True, words)


	def apply_turn(self, turn: Turn, words: list[list[Coordinate]]) -> int:
		newlyPlaced = []

		# Apply letters to real board
		for lp in turn.letters:
			self.get_cell(lp.coordinate).update_letter(lp.letter)
			newlyPlaced.append(lp.coordinate)

		# Mark first placement
		if not self.placedFirst:
			self.placedFirst = True

		# Calculate score
		points = 0
		for word_coords in words:

			points += self.calculate_points(word_coords)

		# 7-tile bonus
		if len(turn.letters) == 7:
			points += 50

		# Track placed tiles
		self.placed.extend([self.get_cell(c) for c in newlyPlaced])

		return points


	def place_word(self, turn: Turn) -> int:
		validation = self.validate_turn(turn)
		print(validation)
		return self.apply_turn(turn, validation.words)


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

			