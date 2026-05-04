

from typing import Optional
from enum import Enum
from modules.scrabble.scrabble_constants import *
from modules.schema import UserFetch
import datetime
from pydantic import BaseModel, model_validator

# Types
class ModifierValue(Enum):
	DOUBLE_LETTER = "DL"
	TRIPLE_LETTER = "TL"
	DOUBLE_WORD = "DW"
	TRIPLE_WORD = "TW"

class DirectionValue(Enum):
	RIGHT = "RIGHT"
	DOWN = "DOWN"

class ValidationResult(BaseModel):
	def __init__(self, valid: bool, words=None):
		self.valid = valid
		self.words = words or []

	def __repr__(self) -> str:
		return f"ValidationResult(valid={self.valid}, words={self.words})"
	

class Coordinate(BaseModel):
	x: int
	y: int

	def __str__(self) -> str:
		return f"({self.x}, {self.y})"

	def __repr__(self) -> str:
		return f"Coordinate(x={self.x}, y={self.y})"
	
	def export(self):
		return (self.x, self.y)
	
	def is_center(self) -> bool:
		return self.x == CENTER[0] and self.y == CENTER[1]
	
class Letter(BaseModel):
	letter: str
	isBlank: bool = False

	@model_validator(mode="after")
	def validate_letter(self):
		self.letter = self.letter.lower()
		return self

	def __repr__(self) -> str:
		return f"Letter(letter=\"{self.letter}\", isBlank={self.isBlank})"
	
class LetterPlace(BaseModel):
	coordinate: Coordinate
	letter: Letter

	
	def __repr__(self) -> str:
		return f"LetterPlace(coordinate={self.coordinate}, letter={self.letter})"

class Turn(BaseModel):
	letters: list[LetterPlace]
	direction: DirectionValue

	def __repr__(self) -> str:
		return f"Turn(letters={self.letters}, direction={self.direction})"
	
class Modifier(BaseModel): 
	modifier: ModifierValue | None
	modifierUsed: bool = False

class Tile(BaseModel):
	letter: Letter
	modifier: Modifier
	coordinate: Coordinate

	def update_letter(self, letter: Letter):
		self.letter = letter

	def __str__(self) -> str:
		return f"Tile(letter=\"{self.letter}\")"

	def __repr__(self) -> str:
		return self.__str__()