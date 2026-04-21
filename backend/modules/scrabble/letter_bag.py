from pathlib import Path
import json, random
from scrabble_types import Letter

LETTER_BAG_PATH = Path.cwd() / "letter_distribution.json"

class LetterBag:

	def __init__(self) -> None:
		self.bag = json.load(open(LETTER_BAG_PATH))
		# Shuffle the bag
		self.shuffle_bag()
		
	def shuffle_bag(self, amount: int=5):
		(random.shuffle(self.bag) for _ in range(amount))

	def take_letters(self, amount: int) -> list[Letter]:
		if amount > len(self.bag):
			amount = len(self.bag)
		sampled = random.sample(self.bag, k=amount)
		return [Letter(letter=letter, isBlank=letter == " ") for letter in sampled]

	def give_letters(self, letters: list[Letter]):
		for letter in letters:
			self.bag.append(letter.letter)
		self.shuffle_bag()

	def replace_letters(self, letters: list[Letter]) -> list[Letter]:
		self.give_letters(letters)
		return self.take_letters(len(letters))
	

