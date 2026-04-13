from .scrabble import Scrabble, arr
from modules.schema import UserFetch, GameOptions, GamePlayer
import copy

class Game:

	def __init__(self, gameID: str, options: GameOptions, leaderID: int) -> None:
		self.id = gameID
		self.leader = leaderID
		self.options = options.model_dump(mode="json")
		self.game = Scrabble(copy.deepcopy(arr))
		self.type = options.game_type
		self.players: list[GamePlayer] = []
		self.hasStarted = False
		if self.type == "GROUP":
			if options.group_size:
				self.groups: list[list[int]] = [[] for _ in range(options.group_size)] # makes array of groups
			else:
				raise Exception("Group size not specified")
		elif self.type == "BOT":
			self.bot = True
		self.dictionary_allowed = options.dictionary
		self.time_limit = options.time_limit
		
	def get_current_turn(self):
		return self.game.fetch_turn()
	
	async def game_turn(self, letters):
		"""
		Places a word on the game board based on the given letters and direction.

		Parameters:
			letters (list[tuple[int, int], str]): A list of coordinates and letters.

		Returns:
			bool | int | Literal[False]: The points gotten by the player for placing the word.
		"""

		firstCoordinate = None
		direction = "RIGHT"
		playerLetters = self.game.fetch_player_letters(self.get_current_turn())
		
		# TODO: identify if the letters used are available, and direction of play.
		blanksIdentified = []
		for [x,y], letter in letters:
			# identify direction
			if firstCoordinate == None:
				firstCoordinate = [x,y]
			else:
				if x-firstCoordinate[0] != 0:
					direction = "RIGHT"
					letters.sort(key=lambda x: x[0][0])
				else:
					direction = "DOWN"
					letters.sort(key=lambda x: x[0][1])
			# identify if player has all available letters.
			if letter in playerLetters:
				playerLetters.remove(letter)
			else:
				# identify if blank is there, and use that.
				blank = " "
				if blank in playerLetters:
					playerLetters.remove(blank)
					blanksIdentified.append((x,y))
				else:
					# invalid placement.
					return False
		print("Player has all letters required for this turn.")
		# this should not have a side effect of moving to the next turn.
		result = await self.game.place_word(letters, direction, blanksIdentified)
		if type(result) == bool:
			return False
		
		# Update letters and return result.
		# get_current_turn should be the same, otherwise place_word changes the current turn.
		self.game.set_player_letters(self.get_current_turn(), playerLetters)
		print(f"result: {result}")
		return result

	def _toGamePlayer(self, player: UserFetch) -> GamePlayer:
		return GamePlayer.model_validate(player)

	def export_data(self):
		# TODO: include scrabble board data
		data =  {
			"leader": self.leader,
			"game_type": self.type,
			"players": [x.model_dump(mode="json") for x in self.players],
			"has_started": self.hasStarted,
			"turn": self.game.fetch_turn(),
			"options": self.options
		}
		if self.type == "GROUP":
			data['groups'] = self.groups
		
		return data
	
	def add_player(self, player: UserFetch):
		"""
			Add a player to the game.
			
			Checks if the game has already started or if the player is already in the game.
			If the game is a normal game, it checks if the game is full (4 players).
			If the game is a group game, it checks if all groups are full (each group has 2 players).
			If the game is a bot game, it checks if there is already a player in the game.
			
			Raises an exception if any of the above conditions are met.
			
			Parameters:
			player (UserFetch): The player to add to the game.
			
			Returns:
			None
		"""
		if self.hasStarted:
			raise Exception("Game has already started")
		player = self._toGamePlayer(player)
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
						# TODO: this needs to adjust for any index not just this scenario
						self.groups[i].append(player.userID)
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
	
	def remove_player(self, player: UserFetch | int):
		"""
			Remove a player from the game.
			
			Args:
				player (UserFetch | int): The player to remove. Can be either a UserFetch object or the player's userID as an integer.
			
			Returns:
				bool: True if the player was removed successfully, False otherwise.
			
			Raises:
				ValueError: If the player is not in the player list.
		"""
		if type(player) == int:
			for i, p in enumerate(self.players):
				if p.userID == player:
					# TODO: pretty sure this errors since modifying a list whilst iterating through it
					self.players.pop(i)
					break
			if self.type == "GROUP":
				for i, group in enumerate(self.groups):
					if player in group:
						self.groups[i].remove(player)
						# only one player per group so can break.
						break
		elif type(player) == UserFetch:
			player = self._toGamePlayer(player)
			try:
				self.players.remove(player)
				if self.type == "GROUP":
					for i, group in enumerate(self.groups):
						if player.userID in group:
							self.groups[i].remove(player.userID)
							# only one player per group so can break.
							break
			except ValueError:
				raise Exception("Player not in player list")
		return True
	
	def in_group(self, player: UserFetch, groupIndex: int):
		return player.userID in self.groups[groupIndex]

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
		if self.hasStarted:
			raise Exception("Game has already started")
		alreadyinGroup = self.in_group(player, groupIndex)
		if alreadyinGroup:
			return alreadyinGroup
		
		# check if adding the player into the group becomes too many.
		if len(self.groups[groupIndex]) + 1 > 2:
			raise Exception("Group is full")
		for i, group in enumerate(self.groups):
			if player.userID in group:
				if i != groupIndex: 
					self.groups[i].remove(player.userID)
				else: 
					alreadyinGroup = True

		if groupIndex > len(self.groups)-1 or groupIndex < 0:
			raise Exception("Group does not exist")
		if not alreadyinGroup:
			self.groups[groupIndex].append(player.userID)
		return True
	
	def leave_group(self, player: UserFetch):
		"""
			Remove a player from a group

			Args:
				player (UserFetch): The player to remove from the group

			Returns:
				bool: Whether the player was successfully removed

			Raises:
				Exception: If the game has already started
				Exception: If the player is not in a group
		"""
		if self.hasStarted:
			raise Exception("Game has already started")
		hasGroup = False
		for i, group in enumerate(self.groups):
			if player.userID in group:
				hasGroup = True
				self.groups[i].remove(player.userID)
		if not hasGroup:
			raise Exception("Player is not in a group")
		return True

	def start_game(self):
		"""
			Start the game

			Initializes the game state and hands out the current turn
			to the players.

			Returns:
				int: The current turn
		"""
		self.hasStarted = True
		currentTurn = self.game.init_game(self.players)
		return currentTurn
	
	def finish_game(self):
		# get all data from the board, input into database, continue
		
		pass