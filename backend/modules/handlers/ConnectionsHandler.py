
from typing import Optional
import secrets
from modules.websocket.WebsocketWrapper import WebsocketWrapper

letterChoice = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"



def generateGameCode():
	return ''.join(secrets.choice(letterChoice) for _ in range(4))

class ConnectionHandler:

	def __init__(self) -> None:
		self.connections: dict[int, WebsocketWrapper] = {}
		# Maps session_id, to user_id
		self.session_ids: dict[str, int] = {}

	# get_connection_or_none
	# get_connection_by_session_id_or_none
	# set_connection
	# remove_connection
	# disconnect connection
	# disconnect_all
	# remove_all
	# disconnect_and_remove_all

	def get_connection_or_none(self, userID: int) -> Optional[WebsocketWrapper]:
		return self.connections.get(userID, None)
	
	def get_connection_by_session_id_or_none(self, session_id: str) -> Optional[WebsocketWrapper]:
		hasUserID = self.session_ids.get(session_id, None)
		if not hasUserID:
			return hasUserID
		return self.get_connection_or_none(hasUserID)
	
	def set_connection(self, websocket: WebsocketWrapper):
		if not websocket.get_authenticated():
			raise Exception("User not authenticated")
		
		userData = websocket.get_user()
		if not userData:
			raise Exception("User data not found")

		self.session_ids[userData.sessionID] = userData.userID
		self.connections[userData.userID] = websocket
		
	def remove_connection_by_user_id(self, userID: int):
		if userID in self.connections:
			del self.connections[userID]
		return

	def remove_connection(self, websocket: WebsocketWrapper):
		if not websocket.get_authenticated():
			# Wouldnt have been in connections anyways
			return
		userData = websocket.get_user()
		if not userData:
			# user doesnt exist anyways
			return 
		self.remove_connection_by_user_id(userData.userID)
	
	async def disconnect_all(self):
		for ws in self.connections.values():
			await ws.close()

	async def remove_all(self):
		for key in self.connections.keys():
			del self.connections[key]
			del self.session_ids[key]
		
	async def disconnect_and_remove_all(self):
		await self.disconnect_all()
		await self.remove_all()


	# OLD DATA

	# def create_game(self, options: GameOptions, leaderID: int):
	# 	"""
	# 	Creates a new game with the given options and leaderID.
		
	# 	Returns the game code of the newly created game.
		
	# 	:raises ValueError: If the game code already exists in the game archive.
	# 	"""
	# 	code = generateGameCode()
	# 	while code in self.games:
	# 		code = generateGameCode()

	# 	options.code = code
	# 	if options.game_type == 'NORMAL':
	# 		self.games[code] = NormalGame(options)
	# 	elif options.game_type == 'GROUP':
	# 		groups = []
	# 		for _ in range(4):
	# 			groups.append([])
	# 		self.games[code] = GroupGame(options, groups)
	# 	else:
	# 		# Bot
	# 		self.games[code] = BotGame(options)
	# 	return code
	
	# def fetch_game(self, code: str) -> Optional[GroupGame | NormalGame | BotGame]:
	# 	if code in self.games:
	# 		return self.games[code]
	# 	return None
		
	
	# async def send_message(self, websocket: WebSocket, message: str):
	# 	try:
	# 		# print(f"Sent message: {websocket.user_id} | Message: {message}") # type: ignore	
	# 		await websocket.send_text(message)
	# 	except Exception as er:
	# 		print("TRIED TO SEND MESSAGE BUT ERROR")
	# 		print(er)
	# 		if websocket.user_id in self.to_send: # type: ignore
	# 			self.to_send[websocket.user_id].append(message) # type: ignore
	# 		else:
	# 			self.to_send[websocket.user_id] = [message] # type: ignore
			
	# async def resend_resume(self, userID: int, websocket: WebSocket):
	# 	if userID in self.to_send:
	# 		for message in self.to_send[userID]:
	# 			await self.send_message(websocket, message)
	# 			await asyncio.sleep(0.5)
	# 		del self.to_send[userID]

	# async def send_direct_message(self, message, userID: int):
	# 	if type(message) == dict:
	# 		message = json.dumps(message)
	# 	if userID in self.connections:
	# 		if not self.connections[userID]['disconnected']:
	# 			print(f"Sending direct message: {message}")
	# 			await self.send_message(self.connections[userID]['websocket'], message)

	# async def broadcast_specific(self, message, users: list[int]):
	# 	if type(message) == dict:
	# 		message = json.dumps(message)
	# 	for userID in users:
	# 		if userID == -2:
	# 			# ignore bot player.
	# 			continue
	# 		if userID in self.connections:
	# 			if not self.connections[userID]['disconnected']:
	# 				print(f"Sent message: {userID} | Message: {message}")
	# 				await self.send_message(self.connections[userID]['websocket'], message)
	# 		else:
	# 			print(f"Unable to send message to {userID} | Message: {message}")

	# async def resume(self, websocket: WebSocket, session_id: str):
	# 	options = [key for key, val in self.connections.items() if val['session_id'] == session_id]
	# 	if not options:
	# 		await self.send_message(websocket, json.dumps(packets.authentication.not_found()))
	# 		return False
	# 	userID = options[0]
	# 	self.connections[userID]['websocket'] = websocket
	# 	await self.send_message(websocket, json.dumps(packets.authentication.identify(session_id)))
	# 	return userID
	
	# async def disconnect(self, userID: int):
	# 	if userID in self.connections:
	# 		self.connections[userID]['disconnected'] = True
		
	
	# async def remove(self, userID: int):
		
	# 	if userID in self.connections:
	# 		try:
	# 			# incase websocket already closing.
	# 			userData = self.connections[userID]
	# 			if userData['game'] is not None:
	# 				await manager.broadcast_specific(packets.start.leave_game(gameID=userData['game'], user=userData['info'].model_dump(mode="json")), [x.userID for x in self.games[userData['game']].players if x.userID != userID])					
	# 				self.games[userData['game']].remove_player(userID)

	# 			await asyncio.sleep(3)
	# 			await self.connections[userID]["websocket"].close()
	# 			self.archive[userID] = self.connections[userID]
	# 			del self.connections[userID]
	# 		except Exception as er:
	# 			print(er)
	# 			pass

	# async def identify(self, websocket: WebSocket, token: str, sessionID: str) -> UserFetch:
	# 	# They are added to connection manager once they have sent through their bearer token for me to identify.
	# 	async for session in get_session():
	# 		resp = await session.execute(select(Token.userID, User).where(and_(Token.bearerTokenID == token, Token.isActive == True)).join(
	# 			User, User.userID == Token.userID
	# 		))
	# 		result = resp.all()
	# 		if not result:
	# 			raise Exception("User not found")
			
			
	# 		userID, userInfo = result[0]
	# 		userData = UserFetch.model_validate(userInfo)
	# 		self.connections[userID] = {
	# 			"websocket": websocket,
	# 			"info": userData,
	# 			"game": None,
	# 			"session_id": sessionID,
	# 			"disconnected": False
	# 		}
	# 		return userData
	# 	raise Exception("Database not initialised")
	
	# def find_user(self, sessionID: str, userID: int):
	# 	# FIX: this has side affects which are not relevant to the func name
	# 	if userID in self.archive:
	# 		if sessionID == self.archive[userID]['session_id']:
	# 			self.connections[userID] = self.archive[userID]
	# 			del self.archive[userID]
	# 			return self.connections[userID]
	# 	return False
	
	# def fetch_connection(self, userID: int) -> Connection | bool:
	# 	if userID in self.connections:
	# 		return self.connections[userID]
	# 	return False

	# def set_game(self, userID: int, gameID: str):
	# 	if userID in self.connections: 
	# 		if gameID in self.games:
	# 			print("set game id")
	# 			self.connections[userID]['game'] = gameID
	# 		else:
	# 			raise Exception("Game does not exist")
	# 	else:
	# 		raise Exception("User not in connection list")
		
	# async def close_all(self):
	# 	for connection in self.connections.values():
	# 		await connection['websocket'].close()

global manager
manager = WebsocketManager()