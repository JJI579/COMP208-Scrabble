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
		self.game = Scrabble(arr.copy())
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
			# Handle checking
			if self.type == "NORMAL":
				if len(self.players) == 4:
					raise Exception("Max amount of players in game")
				self.players.append(player)
			elif self.type == "GROUP":
				maxPlayers = len(self.groups)*2
				if len(self.players) == maxPlayers:
					raise Exception("Max amount of players in game")
				self.players.append(player)
				hasGroup = False
				for i, group in enumerate(self.groups):
					if len(group) == 0:
						self.groups[i].append(player)
						hasGroup = True
						break
				if not hasGroup:
					print("All groups are full...")
					# Should remove player?
					raise Exception("All groups are full")
			else: # bot
				if len(self.players) == 0:
					self.players.append(player)
				else:
					raise Exception("Only one player when Bot Game")
	
	def remove_player(self, player: UserFetch):
		try:
			self.players.remove(player)
			if self.type == "GROUP":
				for i, group in enumerate(self.groups):
					if player in group:
						self.groups[i].remove(player)
						# only one player per group so can break.
						break
			return True
		except ValueError:
			raise Exception("Player not in player list")
		
	def join_group(self, player: UserFetch, groupIndex: int):
		"""
		Join a player to a group

		Removes the player from any other group they are in - so can be used as a move group

		Args:
			player (UserFetch): The player to join the group
			groupIndex (int): The index of the group to join
		Returns:
			bool: Whether the player was successfully joined
		"""
		for i, group in enumerate(self.groups):
			if player in group:
				if i != groupIndex:
					self.groups[i].remove(player)

		if groupIndex > len(self.groups)-1:
			raise Exception("Group does not exist")
		self.groups[groupIndex].append(player)
		return True
	
	def leave_group(self, player: UserFetch):
		hasGroup = False
		for i, group in enumerate(self.groups):
			if player in group:
				hasGroup = True
				self.groups[i].remove(player)
		if not hasGroup:
			raise Exception("Player is not in a group")
		return True