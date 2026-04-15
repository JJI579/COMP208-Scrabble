from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from modules.database.database import get_session, AsyncSession
from modules.functions import get_current_user
from modules.logger import WebsocketLogger
from typing import Annotated, TypedDict
from modules.database.models import User
from modules.schema import GameOptions, PacketType, UserFetch
from modules.websocket.WebsocketManager import manager
from sqlmodel import insert
from modules.database.models import Word
import asyncio, secrets, json
from modules.websocket.packets import packets

router = APIRouter(
	prefix="",
	tags=[],
)

gameRouter = APIRouter(
	prefix="/game",
	tags=["game"],
)


# @gameRouter.get('/words')
# async def addwords(session: AsyncSession = Depends(get_session)):
	
# 	_words = [{'word': x.strip()} for x in open('sowpods.txt', 'r').read().split('\n')]
# 	total = 0

# 	await session.execute(insert(Word), _words)
# 	await session.commit()
	
# 	return {'total': len(_words)}

@gameRouter.post("/create")
async def createGame(options: GameOptions, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	CODE = manager.create_game(options, current_user.userID) # type: ignore
	# Add the creator to the game immediately so they become the leader lobby
	try:
		game = manager.fetch_game(CODE)
		if type(game) != bool:
			game.add_player(UserFetch.model_validate(current_user))
			manager.set_game(current_user.userID, CODE) # type: ignore
			await manager.send_direct_message(packets.start.update_game(game.export_data(), game.id), current_user.userID) # type: ignore
	except Exception as e:
		print("Error setting creator into game:", e)
	# TODO: add to database
	return {
		"code": CODE
	}

wsLogger = WebsocketLogger()

class GameHandler:

	def __init__(self) -> None:
		pass

	@staticmethod
	async def game_start(data: dict, websocket: WebSocket):
		"""
			Handles the game start packet.

			Checks if the game exists and if the user is the game leader.
			If the game exists and the user is the game leader, starts the game and broadcasts to all players that the game has started.
			If the game does not exist, sends an error message to the user.
			If the user is not the game leader, sends an error message to the user.

			Parameters:
				data (dict): The data from the packet.
				websocket (WebSocket): The websocket connection of the user.

			Returns:
				None
		"""
		data = data['d']
		if 'code' not in data:
			await manager.send_message(websocket, json.dumps(packets.start.invalid_game(data['code'])))
			return
		
		game = manager.fetch_game(data['code'])
		if type(game) == bool:
			print("Game does not exist")
			await manager.send_message(websocket, json.dumps(packets.start.invalid_game(data['code'])))
			return False
		
		if game.leader != websocket.user_id: # type: ignore	
			await manager.send_message(websocket, json.dumps(packets.error("Only the leader can start the game!")))
			return

		gameTurn = game.start_game()

		await manager.broadcast_specific(packets.start.start_game(data['code']), [x.userID for x in game.players])

		await asyncio.sleep(.5)
		for x in game.players:
			await GameHandler.game_update(data['code'], x.userID)
			letters = game.game.fetch_player_letters(x.userID)
			ongoing_game_update = packets.during.game_update({
				"turn": gameTurn,
				"letters": letters
			})
			await manager.send_direct_message(ongoing_game_update, x.userID)
	
	@staticmethod
	async def game_turn(data: dict, websocket: WebSocket):
		"""
			Handles the game turn packet.

			Checks if the user is in a game and if it is their turn.
			If the user is in a game and it is their turn, checks if the letters are valid and if they are, updates the game board and broadcasts the updated board to all players.
			If the user is not in a game, sends an error message to the user.
			If the user is in a game but it is not their turn, sends an error message to the user.

			Parameters:
				data (dict): The data from the packet.
				websocket (WebSocket): The websocket connection of the user.

			Returns:
				None
		"""
		try:

			userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
			if type(userConnection) == bool:
				return

			if userConnection['game'] == None:
				errorPacket = packets.error("You are not in a game")
				return await manager.send_message(websocket, json.dumps(errorPacket))
			
			game = manager.fetch_game(userConnection['game'])
			if type(game) == bool:
				return
			if userConnection['info'].userID == game.get_current_turn():
				pointsAmount = await game.game_turn(data['d']['letters'])
				# check if game has finished.
				if type(pointsAmount) == bool:
					print(pointsAmount)
					print("unknown error")
					errorPacket = packets.error("Invalid placement of letters!")
					await manager.send_direct_message(errorPacket, websocket.user_id) # type: ignore
					return
				newGrid = game.game.export_grid()
				nextTurn = game.game.next_turn()

				# Update the board for other players,
				gameUpdatePacket = packets.during.game_update({
					"grid": newGrid,
					"turn": nextTurn,
					# Pretty sure if i add this here the way I have implemented it on the frontend will add it to the player.
					"points": pointsAmount
				})
				await manager.broadcast_specific(gameUpdatePacket, [x.userID for x in game.players if x.userID != websocket.user_id]) # type: ignore
				# Update the board for the user who just played.
				updateCurrentUser = packets.during.game_update({
					"grid": newGrid,
					"turn": nextTurn,
					"points": pointsAmount,
					"letters": game.game.fetch_player_letters(websocket.user_id) # type: ignore
				})	
				await manager.send_direct_message(updateCurrentUser, websocket.user_id) # type: ignore
				# check if the bot is next then make the bot play.
				print("NEXT TURN")
				print(nextTurn)
				if nextTurn == -2: 
					await asyncio.sleep(1)
					print("this is the way")
					botPoints = await game.bot_turn()
					print(botPoints)
					newGrid = game.game.export_grid()
					nextTurn = game.game.next_turn()
					# Update the board for other players,
					gameUpdatePacket = packets.during.game_update({
						"grid": newGrid,
						"turn": nextTurn,
					})
					await manager.broadcast_specific(gameUpdatePacket, [x.userID for x in game.players])
				if game.game.finished:
					return await GameHandler.finish_game(websocket)

			else:
				errorPacket = packets.error("It is not your turn currently!")
				return await manager.send_direct_message(errorPacket, websocket.user_id) # type: ignore
				

		except Exception as e:
			print(e)

	@staticmethod
	async def finish_game(websocket: WebSocket):
		userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
		if type(userConnection) == bool:
			return

		if userConnection['game'] == None:
			errorPacket = packets.error("You are not in a game")
			return await manager.send_message(websocket, json.dumps(errorPacket))
		
		game = manager.fetch_game(userConnection['game'])
		if type(game) == bool:
			return
		
		# game is game object
		gameResult = game.finish_game()
		[x.userID for x in game.players]
		gameFinishPacket = packets.end.game_end(gameResult)

		# TODO: input all data into the user's stats etc
		
		await manager.broadcast_specific(gameFinishPacket, [x.userID for x in game.players if x.userID != websocket.user_id]) # type: ignore

	@staticmethod
	async def player_join(data: dict, websocket: WebSocket):
		
		game = manager.fetch_game(data['d']['code'])
		if type(game) == bool:
			await manager.send_message(websocket, json.dumps(packets.start.invalid_game(data['d']['code'])))
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
			
			# INFO: This error is weird.
			errorPacket = packets.error(er.args[0])
			await manager.send_message(websocket, json.dumps(errorPacket))
			return False
		try:
			manager.set_game(userID, game.id)
		except Exception as er:
			print("trying to set user game but error: ", er)
		sendPacket = packets.start.join_game(gameID=game.id, user=fetchModel.model_dump(mode="json"))
		await manager.broadcast_specific(sendPacket, [x.userID for x in game.players if x.userID != userID])
		await GameHandler.game_update(game.id, websocket)
		return True

	@staticmethod
	async def player_leave(data: dict, websocket: WebSocket):
		userID = websocket.user_id # type: ignore
		user = manager.fetch_connection(userID)
		if type(user) == bool:
			# INFO: if the websocket has managed to send this yet not be authenticated within the manager 
			# class this is like impossible
			# so close their websocket,
			print("websocket should not be existing...")
			errorPacket = packets.error("Your websocket has not been authenticated yet...")
			await manager.send_message(websocket, json.dumps(errorPacket))
			await websocket.close()
			return
		

		if user['game'] == None:
			print("No game exists under the user....")
			return
		
		game = manager.fetch_game(user['game'])
		if type(game) == bool:
			print("the game doesnt exist...")
			return 
		
		sendPacket = packets.start.leave_game(game.id, user['info'].model_dump(mode="json"))
		await manager.broadcast_specific(sendPacket, [x.userID for x in game.players if x.userID != userID])
		leavePacket = packets.start.confirm_leave(game.id)
		await manager.send_direct_message(leavePacket, userID)
		game.remove_player(user['info'])
		

	@staticmethod
	async def game_update(gameID: str, websocket: WebSocket | int):
		game = manager.fetch_game(gameID)
		if type(game) == bool:
			print("game type is bool")
			errorPacket = json.dumps(packets.start.invalid_game(gameID))
			if type(websocket) == int:
				await manager.send_direct_message(errorPacket, websocket)
			elif type(websocket) == WebSocket:
				await manager.send_message(websocket, errorPacket)
			return False
		packetData = packets.start.update_game(game.export_data(), game.id)
		
		await manager.send_direct_message(packetData, websocket.user_id if type(websocket) == WebSocket else websocket) # type: ignore
	
	class GroupJoinData(TypedDict):
		index: int

	@staticmethod
	async def group_join(data: dict, websocket: WebSocket):
		groupIndex = data['d']['index']
		
		userID = websocket.user_id # type: ignore
		userData = manager.connections[userID]['info']
		
		gameCode = manager.connections[userID]['game']
		if gameCode == None:
			# return game doesnt exist
			return
	
		gameData = manager.fetch_game(gameCode)
		if type(gameData) == bool:
			await manager.send_message(websocket, json.dumps(packets.start.invalid_game(gameCode)))
			print("game doesnt exist")
			return
		
		if gameData.hasStarted:
			print("This is a little problem...")
			await manager.send_message(websocket, json.dumps(packets.error("Game has already started...")))
			return
		
		# check if user is in the game
		ids = [x.userID for x in gameData.players]
		if userData.userID not in ids:
			print("they are not in the game...")
			return
		if gameData.in_group(userData, groupIndex):
			# do not need to acknowledge, already in the group - but maybe perform game_update?
			return
		
		try:
			gameData.join_group(userData, groupIndex)
		except Exception as er:
			toSend = packets.error(er.args[0])
			await manager.send_message(websocket, json.dumps(toSend))
			return
		packetData = packets.start.join_group(userData.model_dump(mode="json"), gameData.groups)
		await manager.broadcast_specific(packetData, [x.userID for x in gameData.players])
		

@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
	
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
		elif packetType == "RESUME" and not hasIdentified:
			
			resumeResponse = await manager.resume(websocket, data['d']['session_id'])
			if type(resumeResponse) == bool:
				wsLogger.error("Not found, closing websocket.")
				return await websocket.close()
			userData = manager.fetch_connection(resumeResponse)
			userIdentified = resumeResponse
			wsLogger.info(f"RESUME | WS ID: {websocket.session_id} | User Identified: {userIdentified}") # pyright: ignore[reportAttributeAccessIssue]
			websocket.user_id = userIdentified # pyright: ignore[reportAttributeAccessIssue]
			hasIdentified = True
			if type(userData) != bool:
				# send game update to the user.
				if type(userData['game']) == str:
					await GameHandler.game_update(userData['game'], websocket)
		else:
			if hasIdentified:
				# ignore ping as doesnt help with debug.
				if packetType != "PING":
					print("RECEIVED: ", packetType)
				userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
				if type(userConnection) == bool: # will be false
					print("USER DOES NOT EIXST, REMOVE WEBSOCKET?")
					await manager.send_message(websocket, json.dumps(packets.error("You are not authenticated, Closing websocket.")))
					break # should break to exit while True.
				# else is Connection class
				match (packetType):
					case "PLAYER_JOIN":
						resp = await GameHandler.player_join(data, websocket)
						if not resp:
							continue
						continue
					case "PLAYER_LEAVE":
						await GameHandler.player_leave(data, websocket)
						continue
					case "GAME_UPDATE":
						# Client requesting full game update
						if userConnection['game'] != None:
							userGameCode = userConnection['game']
							await GameHandler.game_update(userGameCode, websocket)
						continue
					case "GROUP_JOIN":
						await GameHandler.group_join(data, websocket)
						continue
					case "GAME_START":
						await GameHandler.game_start(data, websocket)
						
						continue
					case "GAME_TURN":
						await GameHandler.game_turn(data, websocket)
						continue


			else:
				return