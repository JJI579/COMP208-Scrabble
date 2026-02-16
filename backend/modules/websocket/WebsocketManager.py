from fastapi import WebSocket
import json
from typing import Optional
from modules.database.database import get_session
from sqlmodel import select
from sqlalchemy import and_, or_
from modules.database.models import User, Token
from modules.scrabble.game import Game
from modules.schema import GameOptions, UserFetch
from modules.websocket.packets import packets
import asyncio
import secrets

letterChoice = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

from typing import TypedDict
class Connection(TypedDict):
	websocket: WebSocket
	info: UserFetch
	game: Optional[str]
	session_id: str
# {
# 	"websocket": websocket,
# 	"info": userInfo,
# 	"game": None,
# 	"session_id": sessionID,
# }

def generateGameCode():
	return ''.join(secrets.choice(letterChoice) for _ in range(4))

class WebsocketManager:

	def __init__(self) -> None:
		self.connections: dict[int, Connection] = {}
		self.archive = {}
		# gameID, gameClass
		self.games = {}
		# userID, array of packets
		self.to_send = {

		}

	def create_game(self, options: GameOptions, leaderID: int):
		code = generateGameCode()
		while code in self.games:
			code = generateGameCode()
		self.games[code] = Game(code, options, leaderID)
		return code
	
	def fetch_game(self, code: str) -> Game | bool:
		if code in self.games:
			return self.games[code]
		return False
	
	async def send_message(self, websocket: WebSocket, message: str):
		try:
			await websocket.send_text(message)
		except Exception as er:
			print("TRIED TO SEND MESSAGE BUT ERROR")
			print(er)
			if websocket.user_id in self.to_send: # type: ignore
				self.to_send[websocket.user_id].append(message) # type: ignore
			else:
				self.to_send[websocket.user_id] = [message] # type: ignore
			
	async def resend_resume(self, userID: int, websocket: WebSocket):
		if userID in self.to_send:
			for message in self.to_send[userID]:
				await self.send_message(websocket, message)
				await asyncio.sleep(0.5)
			del self.to_send[userID]

	async def send_direct_message(self, message, userID: int):
		if type(message) == dict:
			message = json.dumps(message)
		if userID in self.connections:
			await self.send_message(self.connections[userID]['websocket'], message)

	async def broadcast_specific(self, message, users: list[int]):
		originalMessage = message
		if type(message) == dict:
			message = json.dumps(message)
		for userID in users:
			if userID in self.connections:
				print(f"Sent message: {userID} | Message: {message}")
				await self.send_message(self.connections[userID]['websocket'], message)
			else:
				print(f"Unable to send message to {userID} | Message: {message}")

	# async def broadcast(self, message, userID: Optional[int]=None):
	# 	origMessage = message
	# 	if type(message) == dict:
	# 		message = json.dumps(message)
	# 	if userID is not None:

	# 		# NEED TO MAKE THIS PERSONALISED PER CONNECTION
	# 		if userID in self.connections:
	# 			for toSendID in self.connections[userID]['friends']:
	# 				if toSendID in self.connections:
	# 					await self.send_message(self.connections[toSendID]['websocket'], message)
	# 		if origMessage.get('t') == 'PHOTO_UPDATE':
	# 			if userID in self.connections:
	# 				await self.send_message(self.connections[userID]['websocket'], message)
	# 		else:
	# 			return
	# 	else:
	# 		for connection in self.connections:
	# 			await self.send_message(self.connections[connection]['websocket'], message)

	async def remove(self, userID: int):
		
		if userID in self.connections:
			try:
				# incase websocket already closing.
				userData = self.connections[userID]
				if userData['game'] is not None:
					print("tyhis will be true")
					# echo to game members of player leave
					async for session in get_session():
						print("we are here")
						resp = await session.execute(select(User).where(User.userID == userID))
						# they will exist.
						user = resp.scalar_one()
						
						await manager.broadcast_specific(packets.start.leave_game(gameID=userData['game'], user=UserFetch.model_validate(user).model_dump(mode="json")), [x.userID for x in self.games[userData['game']].players if x.userID != userID])
					
					self.games[userData['game']].remove_player(userID)
				await asyncio.sleep(3)
				await self.connections[userID]["websocket"].close()
				self.archive[userID] = self.connections[userID]
				del self.connections[userID]
			except Exception as er:
				print(er)
				pass

	async def identify(self, websocket: WebSocket, token: str, sessionID: str):
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
					"info": UserFetch.model_validate(userInfo),
					"game": None,
					"session_id": sessionID,
				}
				return userID
	
	def find_user(self, sessionID: str, userID: int):
		# FIX: this has side affects which are not relevant to the func name
		if userID in self.archive:
			if sessionID == self.archive[userID]['session_id']:
				self.connections[userID] = self.archive[userID]
				del self.archive[userID]
				return self.connections[userID]
		return False
	
	def fetch_connection(self, userID: int) -> Connection | bool:
		if userID in self.connections:
			return self.connections[userID]
		return False

	def set_game(self, userID: int, gameID: str):
		if userID in self.connections: 
			if gameID in self.games:
				self.connections[userID]['game'] = gameID
			else:
				raise Exception("Game does not exist")
		else:
			raise Exception("User not in connection list")
		
	async def close_all(self):
		for connection in self.connections.values():
			await connection['websocket'].close()

global manager
manager = WebsocketManager()