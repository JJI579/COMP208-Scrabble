from fastapi.websockets import WebSocket

from sqlalchemy import and_, select, or_
from modules.database import get_session
import json
from typing import Optional

class WebsocketPacket:
	def createPacket(self, packetType: str, content):

		content = {
			't': packetType.upper(),
			'd': content if type(content) == dict else {'text': content} # pyright: ignore[reportCallIssue]
		}
		return content
	
	def create_game(self):
		pass

	def delete_game(self):
		pass

	def accept_invite(self):
		pass

	def reject_invite(self):
		pass

	
	
class WebsocketManager:

	def __init__(self) -> None:
		self.connections = {}
		
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
			# TODO: create identification session_id and send back to the user so they can handle.
			pass
			
	async def close_all(self):
		for connection in self.connections:
			await connection.close()

global manager, packetClass
packetClass = WebsocketPacket()
manager = WebsocketManager()