

from typing import Optional
from enum import Enum
from scrabble_constants import *
from modules.schema import UserFetch
import datetime


# Types
class ModifierValue(Enum):
	DOUBLE_LETTER = "DL"
	TRIPLE_LETTER = "TL"
	DOUBLE_WORD = "DW"
	TRIPLE_WORD = "TW"

class DirectionValue(Enum):
	RIGHT = "RIGHT"
	DOWN = "DOWN"

class ValidationResult:
	def __init__(self, valid: bool, words=None):
		self.valid = valid
		self.words = words or []

	def __repr__(self) -> str:
		return f"ValidationResult(valid={self.valid}, words={self.words})"
	
	


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