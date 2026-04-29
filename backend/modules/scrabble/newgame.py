from newscrab import Scrabble
from modules.schema import UserFetch
from pydantic import BaseModel
import datetime
import copy

from typing import TypeVar, Generic
from scrabble_types import *
from modules.scrabble.letter_bag import LetterBag


# --------------------
# Models
# --------------------

class Player(BaseModel):
	data: UserFetch
	letters: list[Letter] = []
	points: int = 0

# class Group:
# 	players: list
# 	leader: list

class Group(BaseModel):
	players: list[Player]
	leader: Player
	points: int =  0
	letters: list[Letter] = []
	

T = TypeVar("T")  # Turn type (Player or Group)


# --------------------
# Base Game (Generic)
# --------------------

class BaseGame(Generic[T]):

	def __init__(self) -> None:
		self.players: list[Player] = []

		self.turn = 0
		self.letter_bag = LetterBag()
		self.started = False
		self.scrabble = Scrabble()

	# --- Turn handling (must be implemented by subclasses) ---
	def get_current_turn(self) -> T:
		raise NotImplementedError

	def get_next_turn(self) -> T:
		raise NotImplementedError

	# --- Shared game logic ---
	def start_game(self):
		for player in self.get_all_players():
			player.letters = self.letter_bag.take_letters(7)
		self.started = True

	def get_all_players(self) -> list[Player]:
		return self.players

	def verify_letters(self, turn: Turn):
		current = self.get_current_turn()

		# This assumes current has `.letters`
		player_letters = copy.deepcopy(current.letters)

		blank_count = len([l for l in player_letters if l.isBlank])

		for letter_place in turn.letters:
			if letter_place.letter in player_letters:
				player_letters.remove(letter_place.letter)
			else:
				if letter_place.letter.isBlank:
					if blank_count - 1 < 0:
						return False
					blank_count -= 1
				else:
					return False

		return True

	def can_place_word(self, turn: Turn):
		if not self.scrabble.placedFirst:
			if not self.scrabble.valid_first_word_placement(turn):
				return False

		try:
			self.scrabble.validate_turn(turn)
		except Exception:
			return False

		return True

	def place_word(self, turn: Turn):
		if not self.verify_letters(turn):
			raise Exception("Invalid letters")

		if not self.can_place_word(turn):
			raise Exception("Invalid placement")

		return self.scrabble.place_word(turn)

	def give_points_to_current_turn(self, points: int) -> int:
		current = self.get_current_turn()
		current.points += points
		return current.points

	def create_player(self, user: UserFetch) -> Player:
		player = Player(data=user)
		self.players.append(player)
		return player
	
	def fetch_player(self, user: UserFetch) -> Player:
		for player in self.players:
			if player.data.userID == user.userID:
				return player
		raise Exception("Player does not exist")

	def fetch_player_by_id(self, userID: int) -> Player:
		for player in self.players:
			if player.data.userID == userID:
				return player
		raise Exception("Player does not exist")
	
# --------------------
# Normal Game (Player turns)
# --------------------

class NormalGame(BaseGame[Player]):

	def __init__(self) -> None:
		super().__init__()
		self.players: list[Player] = []

	

	def get_current_turn(self) -> Player:
		return self.players[self.turn]

	def get_next_turn(self) -> Player:
		if self.turn + 1 >= len(self.players):
			self.turn = 0
		else:
			self.turn += 1
		return self.players[self.turn]


# --------------------
# Group Game (Group turns)
# --------------------

class GroupGame(BaseGame[Group]):

	def __init__(self, group: list[list[int]]) -> None:
		super().__init__()
		self.players: list[Player] = []
		self.groups: list[Group] = []
		self.partners = {}

	def get_all_players(self) -> list[Player]:
		return self.players

	def get_current_turn(self) -> Group:
		return self.groups[self.turn]

	def get_next_turn(self) -> Group:
		if self.turn + 1 >= len(self.groups):
			self.turn = 0
		else:
			self.turn += 1
		return self.groups[self.turn]

	def add_player_to_group(self, userID: int, groupID: int):
		# Player has to already exist
		player = None
		try:
			player = self.fetch_player_by_id(userID)
		except:
			raise Exception("Player does not exist")
		for i, group in enumerate(self.groups):
			if i == groupID:
				if player not in group.players:
					group.players.append(player)
			else:
				if player in group.players:
					group.players.remove(player)
		# Would be added.

	def start_game(self):
		partners = {}
		for group in self.groups:
			if len(group.players) > 1:
				partners[group.players[0].data.userID] = group.players[1].data.userID
				partners[group.players[1].data.userID] = group.players[0].data.userID
			group.letters = self.letter_bag.take_letters(7)	
		self.partners = partners
		self.started = True

	def get_partner_by_id(self, userID: int) -> Optional[int]:
		if userID in self.partners:
			return self.partners[userID]
		return None

	def get_group_by_id(self, userID: int) -> Optional[Group]:
		for group in self.groups:
			for player in group.players:
				if player.data.userID == userID:
					return group
		return None

# --------------------
# Bot Game (Player turns)
# --------------------

class BotGame(BaseGame[Player]):

	def __init__(self, user: UserFetch) -> None:
		super().__init__()
		self.players: list[Player] = []

		self.create_player(user)

		bot_data = {
			"userID": -2,
			"userName": "Bot",
			"userCreatedAt": datetime.datetime.now(),
			"wins": 0,
			"loses": 0,
			"totalScore": 0,
			"bestScore": 0
		}

		bot = UserFetch.model_validate(bot_data)
		self.create_player(bot)

	def get_current_turn(self) -> Player:
		return self.players[self.turn]

	def get_next_turn(self) -> Player:
		if self.turn + 1 >= len(self.players):
			self.turn = 0
		else:
			self.turn += 1
		return self.players[self.turn]