from scrabble import Scrabble, arr
from typing import Literal, TypedDict, Optional
from modules.schema import UserFetch

GAME_TYPE = Literal[
	"NORMAL",
	"GROUP",
	"BOT"
]

class GameOptions(TypedDict):
	game_type: GAME_TYPE
	group_size: Optional[int]
	time_limit: str | bool
	dictionary: bool # whether dictionary is allowed


class Game:

	def __init__(self, options: GameOptions) -> None:
		self.game = Scrabble(False, arr.copy())
		self.type = options['game_type']
		self.players = []
		if self.type == "GROUP":
			if options['group_size']:
				self.groups = [[] for _ in range(options["group_size"])] # makes array of groups
			else:
				raise Exception("Group size not specified")
		elif self.type == "BOT":
			self.bot = True
		self.dictionary_allowed = options['dictionary']
		self.time_limit = options['time_limit']

	def add_player(self, player: UserFetch):
		if player in self.players:
			raise Exception("Player already in game")
		else:
			if self.type == "NORMAL":
				self.players.append(player)
			elif self.type == "GROUP":
				self.players.append(player)
				self.groups[0].append(player)
			elif self.type == "BOT":
				if len(self.players) == 0:
					self.players.append(player)
				else:
					raise Exception("Only one player when Bot Game")