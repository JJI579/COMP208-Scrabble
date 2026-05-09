from modules.scrabble.newgame import BaseGame
from typing import Optional

class GameHandler:
	def __init__(self):
		self.games: dict[str, BaseGame] = {}

	def set_game(self, code: str, game: BaseGame):
		self.games[code] = game
	
	def get_game(self, code: str) -> Optional[BaseGame]:
		return self.games.get(code, None)
	
	def delete_game(self, code: str):
		if self.get_game(code):
			del self.games[code]
		

	
	