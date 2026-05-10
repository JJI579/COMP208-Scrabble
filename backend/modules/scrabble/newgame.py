from modules.scrabble.newscrab import Scrabble
from modules.schema import UserFetch
from pydantic import BaseModel, Field, model_validator
import datetime
import copy

from typing import Any, TypeVar, Generic, Union
from modules.scrabble.scrabble_types import *
from modules.scrabble.letter_bag import LetterBag
from modules.schema import GameOptions


# --------------------
# Models
# --------------------

class Player(BaseModel):
	id: int = -1
	data: UserFetch
	letters: list[Letter] = Field(default_factory=list)
	points: int = 0

	@model_validator(mode="after")
	def validate_player(self):
		self.id = self.data.userID
		return self
	
# class Group:
# 	players: list
# 	leader: list

class Group(BaseModel):
	players: list[Player] = Field(default_factory=list)
	leader: Player
	points: int =  0
	letters: list[Letter] = Field(default_factory=list)
	

A = TypeVar("A", Group, Player)  # Turn type (Player or Group)


# --------------------
# Base Game (Generic)
# --------------------

class BaseGame(Generic[A]):

	def __init__(self, options: GameOptions) -> None:
		self.id = options.code if options.code else "NONE"
		self.players: list[Player] = []
		self.leaderID: int = -1
		self.turn = 0
		self.letter_bag = LetterBag()
		self.started = False
		self.scrabble = Scrabble()
		self.options = options
		self.finishes = 0


	# --- Turn handling (must be implemented by subclasses) ---
	
	def get_current_turn(self) -> A:
		raise NotImplementedError

	def get_next_turn(self) -> A:
		raise NotImplementedError

	# --- Shared game logic ---
	def start_game(self):

		self.finishesAt = datetime.datetime.now().timestamp() + int(self.options.time_limit)
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

	def get_started(self):
		return self.started
	
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


	def create_player(self, user: UserFetch) -> Player:
		player = Player(data=user)
		if len(self.players) == 0:
			self.leaderID = user.userID
		self.players.append(player)
		return player
	
	def fetch_player(self, user: UserFetch) -> Player:
		return self.fetch_player_by_id(user.userID)

	def fetch_player_by_id(self, userID: int) -> Player:
		for player in self.players:
			if player.data.userID == userID:
				return player
		raise Exception("Player does not exist")

	
	def export_players(self) -> list[dict]:
		data = []
		for player in self.players:
			data.append(player.model_dump(mode="json"))
		return data
		

	def export_game(self) -> dict:
		data = {
			"grid": self.scrabble.export_grid(),
			"leader": self.leaderID,
			"game_type": self.options.game_type,
			"players": self.export_players(),
			"has_started": self.started,
			"turn": self.get_current_turn().model_dump(mode="json"),
			"options": self.options.model_dump(mode="json"),
			"finishes": self.finishes
		}
		return data
	
	def get_id(self):
		return self.id
	
	def get_type(self):
		return self.options.game_type
	

# --------------------
# Normal Game (Player turns)
# --------------------
class NormalGame(BaseGame[Player]):

	def __init__(self, options: GameOptions) -> None:
		
		super().__init__(options)
		self.players: list[Player] = []

	def get_current_turn(self) -> Player:
		return self.players[self.turn]

	def get_next_turn(self) -> Player:
		if self.turn + 1 >= len(self.players):
			self.turn = 0
		else:
			self.turn += 1
		return self.players[self.turn]

	def give_points_to_current_turn(self, points: int) -> int:
		current: Player = self.get_current_turn()
		current.points += points
		return current.points
	
# --------------------
# Group Game (Group turns)
# --------------------

class GroupGame(BaseGame[Group]):

	def __init__(self, options: GameOptions, groups: list[Group]) -> None:
		super().__init__(options)
		self.players: list[Player] = []
		self.groups: list[Group] = groups
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

	def give_points_to_current_turn(self, points: int) -> int:
		current: Group = self.get_current_turn()
		current.points += points
		return current.points
	
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

	def export_game(self) -> dict:
		data = super().export_game()
		data['groups'] = [x.model_dump(mode="json") for x in self.groups]
		if self.started:
			data['partners'] = self.partners
		return data
	
# --------------------
# Bot Game (Player turns)
# --------------------

class BotGame(BaseGame[Player]):

	def __init__(self, options: GameOptions) -> None:
		super().__init__(options)
		self.players: list[Player] = []
		
	def get_current_turn(self) -> Player:
		return self.players[self.turn]

	def get_next_turn(self) -> Player:
		if self.turn + 1 >= len(self.players):
			self.turn = 0
		else:
			self.turn += 1
		return self.players[self.turn]
	
	def start_game(self):

		if len(self.players) == 0:
			raise Exception("Player is not in the game yet")
		
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
		return super().start_game()