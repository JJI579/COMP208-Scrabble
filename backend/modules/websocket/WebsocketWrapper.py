from fastapi import WebSocket
from modules.schema import UserFetch
from typing import Optional
import secrets
from modules.scrabble.newgame import BaseGame

class WebsocketWrapper:

	def __init__(self, ws: WebSocket):
		self.websocket = ws

		# Supposedly Private
		self._user: Optional[UserFetch] = None
		self._sessionID = secrets.token_hex(20)
		self._game: Optional[BaseGame]

	async def accept(self):
		await self.websocket.accept()
	
	async def receive_json(self):
		return await self.websocket.receive_json()
	
	async def close(self):
		return await self.websocket.close()
	
	async def send(self, message: dict):
		return await self.websocket.send_json(message)


	# Setters
	def set_user(self, user: UserFetch):
		self._user = UserFetch

	def set_game(self, game: BaseGame):
		self._game = game

	# Getters
	def get_user(self) -> Optional[UserFetch]:
		return self._user
	
	def get_authenticated(self):
		return self._user is not None
	
	def get_session_id(self):
		return self._sessionID
	
