# This creates games
from modules.scrabble.newgame import BotGame, NormalGame, GroupGame

from modules.schema import GameOptions

class CreationHandler:
	
	def __init__(self):
		pass

	def create_game(self, options: GameOptions) -> NormalGame:
		return NormalGame(options)
	
	def create_bot_game(self, options: GameOptions) -> BotGame:
		return BotGame(options)

	def create_group_game(self, options: GameOptions) -> GroupGame:
		return GroupGame(options)
	
    