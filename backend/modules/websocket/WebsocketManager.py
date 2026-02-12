from fastapi import WebSocket
import json
from typing import Optional
from modules.database.database import get_session
from sqlmodel import select
from sqlalchemy import and_, or_
from modules.database.models import User, Token
from modules.scrabble.game import Game
from modules.schema import GameOptions


import secrets

letterChoice = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def generateGameCode():
	return ''.join(secrets.choice(letterChoice) for _ in range(4))

class WebsocketManager:

	def __init__(self) -> None:
		self.connections = {}
		# gameID, gameClass
		self.games = {}

	def create_game(self, options: GameOptions):
		code = generateGameCode()
		while code in self.games:
			code = generateGameCode()
		self.games[code] = Game(options)
		return code
	
	def fetch_game(self, code: str) -> Game | bool:
		if code in self.games:
			return self.games[code]
		return False
	
	async def send_message(self, websocket: WebSocket, message: str):
		await websocket.send_text(message)

	async def send_direct_message(self, message, userID: int):
		if type(message) == dict:
			message = json.dumps(message)
		if userID in self.connections:
			await self.send_message(self.connections[userID]['websocket'], message)

	async def broadcast(self, message, userID: Optional[int]=None):
		origMessage = message
		if type(message) == dict:
			message = json.dumps(message)
		if userID is not None:

			# NEED TO MAKE THIS PERSONALISED PER CONNECTION
			if userID in self.connections:
				for toSendID in self.connections[userID]['friends']:
					if toSendID in self.connections:
						await self.send_message(self.connections[toSendID]['websocket'], message)
			if origMessage.get('t') == 'PHOTO_UPDATE':
				if userID in self.connections:
					await self.send_message(self.connections[userID]['websocket'], message)
			else:
				return
		else:
			for connection in self.connections:
				await self.send_message(self.connections[connection]['websocket'], message)

	async def remove(self, userID: int):
		if userID in self.connections:
			try:
				# incase websocket already closing.
				await self.connections[userID]["websocket"].close()
			except:
				pass
			del self.connections[userID]

	async def identify(self, websocket: WebSocket, token: str):
		# They are added to connection manager once they have sent through their bearer token for me to identify.
		async for session in get_session():
			resp = await session.execute(select(Token.userID, User).where(and_(Token.bearerTokenID == token, Token.isActive == True)).join(
				User, User.userID == Token.userID
			))
			result = resp.all()
			if not result: 
				# close websocket.
				return False
			else:
				userID, userInfo = result[0]
				self.connections[userID] = {
					"websocket": websocket,
					"info": userInfo,
					"game": None
				}
				return userID
			
	async def close_all(self):
		for connection in self.connections:
			await connection.close()

global manager
manager = WebsocketManager()