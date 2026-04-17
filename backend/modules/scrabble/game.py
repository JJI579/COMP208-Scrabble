from .scrabble import Scrabble, arr
from modules.schema import UserFetch, GameOptions, GamePlayer, GAME_TYPE, BotPlayer
import copy

class Game:

	def __init__(self, gameID: str, options: GameOptions, leaderID: int) -> None:
		self.id = gameID
		self.leader = leaderID
		self.options = options.model_dump(mode="json")
		self.game = Scrabble(copy.deepcopy(arr))
		self.type: GAME_TYPE = options.game_type
		self.players: list[GamePlayer | BotPlayer] = []
		self.hasStarted = False
		self.groups = []
		if self.type == "GROUP":
			if options.group_size:
				self.groups: list[list[int]] = [[] for _ in range(options.group_size)] # makes array of groups
			else:
				raise Exception("Group size not specified")
		elif self.type == "BOT":
			self.bot = True
		self.dictionary_allowed = options.dictionary
		self.time_limit = options.time_limit
		
		# index of the group leaders in self.groupPlayers
		self.groupTurn = 0
		# group leader's userID
		self.groupPlayers = []
	
	def mm_give_points(self, points: int):
		gameTurn = self.mm_get_current_turn()
		print(f"Trying to give {gameTurn} points {points}")
		try:
			self.players[gameTurn].points += points
		except Exception as er:
			print("did not give points?")
			print(er)
		return points


	def mm_get_current_turn(self):		
		"""
		Returns the current turn of the game.

		If the game type is GROUP, return the userID of the current group leader.
		Otherwise, return the result of calling self.game.fetch_turn().
		"""
		if self.type == "GROUP":
			userID = self.groupPlayers[self.groupTurn]
			return userID
		else:
			return self.game.fetch_turn()
	
	def mm_next_turn(self):
		# THIS IS A MIDDLE-MAN to separate between groups and normal
		"""
		Advances the game state to the next player's turn.

		If the game type is GROUP, cycles through the group leaders.
		Otherwise, calls the next_turn() method of the game object.

		Returns the userID of the player whose turn it now is.
		"""
		if self.type == "GROUP":
			print(self.groupTurn)
			
			if (self.groupTurn + 1) == len(self.groupPlayers):
				self.groupTurn = 0
			else:
				self.groupTurn += 1
			return self.mm_get_current_turn()
		else:
			return self.game.next_turn()
		
	async def bot_turn(self):
		resp = await self.game.bot_turn()
		if type(resp) == bool:
			if resp:
				self.game.next_turn()
				# bot has skipped
				pass
			else:
				pass
				# finish the game as bot has had too many passes
			return False
		# update bot score in the wrapper model
		if len(self.players) > self.game.gameTurn:
			self.players[self.game.gameTurn].points += resp
		return resp
	
	def get_group_leader_id(self, userID: int):
		for group in self.groups:
			if userID in group:
				return group[0]
		# This shouldnt return false


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
		playerLetters = copy.deepcopy(self.game.fetch_player_letters(self.mm_get_current_turn()))
		
		blanksIdentified = []
		for [x,y], letter, blankReplacement in letters:
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
					# Invalid placement, deep copied the player's letters to not affect their actual deck unless it works.
					print("Invalid placement, deep copied the player's letters to not affect their actual deck unless it works")
					return False
		print("Player has all letters required for this turn.")
		# this should not have a side effect of moving to the next turn.
		result = await self.game.place_word(letters, direction, blanksIdentified)
		if type(result) == bool:
			print("here")
			return False
		
		# Update letters and return result.
		# get_current_turn should be the same, otherwise place_word changes the current turn.
		self.game.set_player_letters(self.mm_get_current_turn(), playerLetters)
		
		self.mm_give_points(result)
		
		
		# self.players[self.game.gameTurn].points += result
		print(self.players)
		print(f"result: {result}")
		
		
		return result


	def _toGamePlayer(self, player: UserFetch) -> GamePlayer:
		return GamePlayer.model_validate(player)

	def export_data(self):

		grid = self.game.export_grid()
		data =  {
			"grid": grid,
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
	
	def add_bot(self):
		if len(self.players) == 0:
			raise Exception("No players in game to add bot into the game")
		else:
			self.players.append(BotPlayer())

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
					# TODO: pretty sure this errors since modifying a list whilst iterating through it - confirm this
					self.players.pop(i)
					break
			if self.type == "GROUP":
				for i, group in enumerate(self.groups):
					if player in group:
						self.groups[i].remove(player)
						# only one player per group so can break.
						break
		elif isinstance(player, UserFetch):
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
		if self.type == "BOT":
			self.add_bot()

		elif self.type == "GROUP":
			self.partners = {}
			for i, group in enumerate(self.groups):
				if len(group) == 2:
					# if the group is a group with a partner
					self.partners[group[0]] = group[1]
					self.partners[group[1]] = group[0]
		self.hasStarted = True
		if self.type == "GROUP":
			# only want to start the game with the leaders
			players = []
			for group in self.groups:
				if len(group) >= 1:
					groupLeaderID = group[0]
					players.append([x for x in self.players if x.userID == groupLeaderID][0])
			currentTurn = self.game.init_game(players)
			# Because it is a group it has a different turn system handled in this file.
			self.groupPlayers = [x[0] for x in self.groups if len(x) > 0]
			self.groupTurn = 0
		else:
			currentTurn = self.game.init_game(self.players)
		currentTurn = self.mm_get_current_turn()
		print(currentTurn)
		return currentTurn
	
	def get_partner(self, userID: int) -> int | bool:
		if userID in self.partners:
			return self.partners[userID]
		return False
	
	def finish_game(self) -> dict:
		# get all data from the board, input into database, continue
		
		# TO RETURN
		"""
		GRID
		PLAYER SCORE
		PLAYER WORDS

		OTHER PLAYERS SCORES + YOUR OWN FOR LEADERBOARD

		"""

		grid = self.game.export_grid()
		players = [x.dump_json() for x in self.players]
		# players sorted in order of 1st,2nd,3rd etc.
		players.sort(key=lambda x: x['points'], reverse=True)
		winner = max(self.players, key=lambda x: x.points)
		return {
			"grid": grid,
			"players": players,
			"winner": winner,
		}