from fastapi import APIRouter, WebSocket
from fastapi import Depends, WebSocketDisconnect
from modules.database.database import get_session
from modules.database.database import AsyncSession
from modules.functions import get_current_user
from modules.websocket.WebsocketManager import manager
from modules.logger import WebsocketLogger
from typing import Annotated
from modules.database.models import User
from modules.schema import GameOptions, PacketType
from modules.websocket.WebsocketManager import manager
from modules.scrabble.game import Game
import secrets
from sqlmodel import select
from modules.database.models import User
from modules.schema import UserFetch
import asyncio
import json

router = APIRouter(
	prefix="",
	tags=[],
)

gameRouter = APIRouter(
	prefix="/game",
	tags=["game"],
)

@gameRouter.post("/create")
async def createGame(options: GameOptions, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):	
	CODE = manager.create_game(options, current_user.userID) # type: ignore
	return {
		"code": CODE
	}

wsLogger = WebsocketLogger();

from modules.websocket.packets import packets

class GameHandler:

	def __init__(self) -> None:
		pass

	@staticmethod
	async def player_join(data: dict, websocket: WebSocket):
		print("player join")
		print(data)
		game = manager.fetch_game(data['d']['code'])
		
		if type(game) == bool:
			print("Game does not exist")
			await manager.send_message(websocket, json.dumps(packets.start.invalid_game(data['d']['code'])))
			# TODO: send error message
			return False
		userID = websocket.user_id # type: ignore
		userData = manager.connections[userID]['info']
		fetchModel = UserFetch.model_validate(userData)
		try:
			game.add_player(fetchModel)
			manager.set_game(userID, game.id)
		except Exception as er:
			if er.args[0] == "Player already in game":
				sendPacket = packets.start.join_game(gameID=game.id, user=fetchModel.model_dump(mode="json"))
				await GameHandler.game_update(game.id, websocket)
				await manager.broadcast_specific(sendPacket, [x.userID for x in game.players if x.userID != userID])
				return True
			else:
				print("Error with game not exsiting.")
			print(f"error: {er}")
			# TODO: send error message
			return False
		sendPacket = packets.start.join_game(gameID=game.id, user=fetchModel.model_dump(mode="json"))
		await manager.broadcast_specific(sendPacket, [x.userID for x in game.players if x.userID != userID])
		await GameHandler.game_update(game.id, websocket)
		return True

	@staticmethod
	async def player_leave(data: dict, websocket: WebSocket):
		userID = websocket.user_id # type: ignore
		user = manager.fetch_connection(userID)
		if not user:
			print("websocket should not be existing...")
			# TODO: websocket should not be existing...
			return
		
		if not user['game']:
			print("No game exists under the user....")
			return
		
		game = manager.fetch_game(user['game'])
		if type(game) == bool:
			print("the game doesnt exist...")
			return 
		
		sendPacket = packets.start.leave_game(game.id, user['info'])
		await manager.broadcast_specific(sendPacket, [x.userID for x in game.players if x.userID != userID])
		game.remove_player(user['info'])
		

	@staticmethod
	async def game_update(gameID: str, websocket: WebSocket):
		game = manager.fetch_game(gameID)
		if type(game) == bool:
			print("game type is bool")
			# TODO: send error message
			return False
		packetData = packets.start.update_game(game.export_data(), game.id)
		await manager.send_direct_message(packetData, websocket.user_id) # type: ignore
		
@router.websocket('/ws1')
async def websocket_endpoint_v2(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
	hasIdentified = False
	sessionID = secrets.token_hex(20)
	await websocket.accept()
	websocket.session_id = sessionID # type: ignore
	while True:
		try:
			data = await websocket.receive_json()
		except WebSocketDisconnect:
			print("it has disconnected")
			return
		packetType: PacketType = data.get('t', '')
		if packetType == "IDENTIFY" and not hasIdentified:
			identifyResponse = await manager.identify(websocket, data['d']['token'], sessionID)
			if not identifyResponse:
				wsLogger.error("Not found, closing websocket.")
				return await websocket.close()
			userIdentified = identifyResponse
			wsLogger.info(f"WS ID: {websocket.session_id} | User Identified: {userIdentified}") # pyright: ignore[reportAttributeAccessIssue]
			websocket.user_id = userIdentified # pyright: ignore[reportAttributeAccessIssue]
			await manager.send_direct_message(packets.authentication.identify(websocket.session_id), userIdentified) # type: ignore
			hasIdentified = True
		else:
			if hasIdentified:
				match (packetType):

					case "PLAYER_JOIN":
						resp = await GameHandler.player_join(data, websocket)
						if not resp:
							continue
					case "PLAYER_LEAVE":
						print("player left game.")
						userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
						print(userConnection)
						continue
					case "GAME_UPDATE":
						# Client requesting full game update
						userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
						print(userConnection)
						break
						# await GameHandler.game_update()
						
			else:
				return
	

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
	print("Websocket found")
	sessionID = secrets.token_hex(10)
	await websocket.accept()
	await asyncio.sleep(1)
	websocket.session_id = sessionID # type: ignore
	wsLogger.info(f'New Websocket: {websocket.session_id} | Websocket accepted.') # type: ignore
	userIdentified = False
	while True:
		try:
			data = await websocket.receive_json()
			packetType: PacketType = data.get('t', '')
			print("PACKET TYPE: ", packetType)
			if packetType == "IDENTIFY" and not userIdentified:
				identifyResponse = await manager.identify(websocket, data['d']['token'], sessionID) # type: ignore
				if not identifyResponse:
					wsLogger.error("Not found, closing websocket.")
					return await websocket.close()
				userIdentified = identifyResponse
				wsLogger.info(f"WS ID: {websocket.session_id} | User Identified: {userIdentified}") # pyright: ignore[reportAttributeAccessIssue]
				websocket.user_id = userIdentified # pyright: ignore[reportAttributeAccessIssue]
				await manager.send_direct_message(packets.authentication.identify(websocket.session_id), userIdentified) # type: ignore
			elif packetType == "RESUME" and not userIdentified:
				print(data)
				
				userData = manager.find_user(data['d']['sessionID'], data['d']['userID'])
				if type(userData) == bool:
					await websocket.send_json(packets.authentication.not_found())
				else:
					print("User has been found and resumed")
					websocket.user_id = userData['info'].userID # type: ignore
					websocket.session_id = data['d']['sessionID'] # type: ignore
					userIdentified = True
					await manager.resend_resume(userData['info'].userID, websocket) # type: ignore
			else:

				if userIdentified:
					print("User has been identified, listen for it here.")
					match (packetType):

						case "PLAYER_JOIN":
							# person wants to join match
							gameCode = data['d']['code']
							game: Game | bool = manager.fetch_game(gameCode)
							if type(game) == bool:
								wsLogger.error(f"WS ID: {websocket.session_id} | Game not found: {data['d']['code']}") # pyright: ignore[reportAttributeAccessIssue]
								continue
							try:
								# Checking if the user exists
								resp = await session.execute(select(User).where(User.userID == websocket.user_id)) # type: ignore
								userObj = resp.scalar_one()
								userJSON: UserFetch = UserFetch.model_validate(userObj)
								# This will throw an exception if they cannot join because of the game.
								manager.set_game(websocket.user_id, gameCode) # type: ignore
								game.add_player(userJSON)
								thePacket = packets.start.join_game(gameCode, userJSON.model_dump(mode="json"))
								await manager.broadcast_specific(thePacket, [x.userID for x in game.players if x.userID != websocket.user_id]) # type: ignore
								# Send new player the game info alongside their accepted request to join the game.
								gameInfoPacket = thePacket
								gameInfo = game.export_data()
								gameInfoPacket['d']['game'] = gameInfo
								await manager.send_direct_message(gameInfoPacket, websocket.user_id) # type: ignore
							except Exception as er:
								if er.args[0] == "Player already in game":
									print("yes")
									# make em join
									resp = await session.execute(select(User).where(User.userID == websocket.user_id)) # type: ignore
									userObj = resp.scalar_one()
									userJSON: UserFetch = UserFetch.model_validate(userObj)
									thePacket = packets.start.join_game(gameCode, userJSON.model_dump(mode="json"))
									gameInfoPacket = thePacket
									gameInfo = game.export_data()
									gameInfoPacket['d']['game'] = gameInfo
									await manager.send_direct_message(gameInfoPacket, websocket.user_id) # type: ignore
								else:
									print("closing the websocket ln 108")
									await websocket.close()
									wsLogger.error(f"ERROR | WS ID: {websocket.session_id} | Error: {er}") # pyright: ignore[reportAttributeAccessIssue]
								# TODO: send error packet.
								continue

				else:
					wsLogger.info(f"Closing Websocket: {websocket.session_id} | Attempted to send data when Unauthenticated") # pyright: ignore[reportAttributeAccessIssue]
					await websocket.close()
					return
		except WebSocketDisconnect as disconnectedError:
			print("WEBSOCKET DISCONNECTED")
			print(disconnectedError)


		except Exception as e:
			print("we are here..")
			print(e)
			wsLogger.error(f"{websocket.session_id} | Error: {e}") # type: ignore
			try:
				potentialID	 = getattr(websocket, "user_id")
				if potentialID:
					wsLogger.info(f"WS ID: {websocket.session_id} | Removed from active connections: {potentialID}") # type: ignore
					await manager.remove(potentialID)
			except AttributeError:
				break
			break