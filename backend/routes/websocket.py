from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from modules.database.database import get_session, AsyncSession
from modules.functions import get_current_user
from modules.logger import WebsocketLogger
from typing import Annotated, TypedDict
from modules.database.models import User
from modules.schema import GameOptions, PacketType, UserFetch
from modules.websocket.WebsocketManager import manager
from sqlmodel import select
import asyncio, secrets, json
from modules.websocket.packets import packets
from modules.scrabble.game import Game

import copy

import re

# Word filter
def censor_word(word):
    if len(word) <= 2:
        return word
    return word[0] + "*" * (len(word) - 2) + word[-1]

def profanity_filter(message):
    bad_words = [
        "fuck", "shit", "bitch", "asshole", "bastard", "dick", "piss", "crap"
    ]
    
    def replace(match):
        return censor_word(match.group())
    
    pattern = re.compile(r'\b(' + '|'.join(bad_words) + r')\b', re.IGNORECASE)
    return pattern.sub(replace, message)


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

	if options.time_limit == "none":
		options.time_limit = 999999999
	elif options.time_limit == "45":
		options.time_limit = 2700
	elif options.time_limit == "1":
		options.time_limit = 3600
	elif options.time_limit == "2":
		options.time_limit = 7200
	
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

		await manager.broadcast_specific(packets.start.update_game(game.export_data(), game.id), [x.userID for x in game.players])
		await manager.broadcast_specific(packets.start.start_game(data['code']), [x.userID for x in game.players])

		await asyncio.sleep(.5)
		for x in game.players:
			if x.userID == -2:
				continue
			await GameHandler.game_update(data['code'], x.userID)
			letterOwnerID = None
			if game.type == "GROUP":
				checkResponse = game.get_group_leader_id(x.userID)
				if checkResponse == None:
					# This shouldnt happen
					# TODO: RETURN ERROR SAYING THAT USER CANNOT BE FOUND?
					return
				else:
					letterOwnerID = checkResponse
					del checkResponse
			else:
				letterOwnerID = x.userID
			letters = game.game.fetch_player_letters(letterOwnerID)
			ongoing_game_update = packets.during.game_update({
				"turn": gameTurn,
				"letters": letters
			})
			if letterOwnerID == None:
				# ignore it since it isnt your go
				pass
			else:
				# check if the gameTurn == letterOwnerID and if it does set it to the user ID
				if letterOwnerID == gameTurn:
					# set it to your user ID
					ongoing_game_update['d']['turn'] = x.userID
					print("set currentl turn to that users!")
			await manager.send_direct_message(ongoing_game_update, x.userID)

		if game.game.finished:
			return await GameHandler.finish_game(game=game)
	
	@staticmethod
	async def skip_turn(data: dict, websocket: WebSocket):
		# move turn to the next person
		userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
		if type(userConnection) == bool:
			errorPacket = packets.error("You are not authenticated.")
			return await manager.send_message(websocket, json.dumps(errorPacket))

		if userConnection['game'] == None:
			errorPacket = packets.error("You are not in a game")
			return await manager.send_message(websocket, json.dumps(errorPacket))
		
		game = manager.fetch_game(userConnection['game'])
		if type(game) == bool:
			errorPacket = packets.error("You are not in a game")
			return await manager.send_message(websocket, json.dumps(errorPacket))
		
		userID = userConnection['info'].userID
		currentTurn = game.mm_get_current_turn()
		groupLeaderID = game.get_group_leader_id(userID) if game.type == "GROUP" else userID
		if userID != currentTurn and groupLeaderID != currentTurn:
			return await manager.send_direct_message(
				packets.error("It is not your turn currently!"),
				userID
			)
		game.register_skip(userID)
		nextTurn = game.mm_next_turn()

		skipPacket = packets.during.game_update({
			"turn": nextTurn,
			"skipped": True
		})

		await manager.broadcast_specific(
			skipPacket,
			[x.userID for x in game.players]
		)

		""" if game.type == "GROUP":
			for player in game.players:
				await manager.send_direct_message(skipPacket, player.userID) """
		
		if game.game.finished:
			return await GameHandler.finish_game(websocket)

		if game.type == 'BOT' and nextTurn == -2:
				print("next turn after skip:", nextTurn)
				print("game type:", game.type)
				await manager.broadcast_specific(skipPacket, [x.userID for x in game.players])
				return await GameHandler.bot_turn_handler(game, websocket)

	@staticmethod
	async def switch_turn(data: dict, websocket: WebSocket):
		userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
		if type(userConnection) == bool:
			errorPacket = packets.error("You are not authenticated.")
			return await manager.send_message(websocket, json.dumps(errorPacket))

		if userConnection['game'] == None:
			errorPacket = packets.error("You are not in a game")
			return await manager.send_message(websocket, json.dumps(errorPacket))
		
		game = manager.fetch_game(userConnection['game'])
		if type(game) == bool:
			errorPacket = packets.error("You are not in a game")
			return await manager.send_message(websocket, json.dumps(errorPacket))

		userID = userConnection['info'].userID
		currentTurn = game.mm_get_current_turn()
		groupLeaderID = game.get_group_leader_id(userID) if game.type == "GROUP" else userID
		if userID != currentTurn and groupLeaderID != currentTurn:
			return await manager.send_direct_message(
				packets.error("It is not your turn currently!"),
				userID
			)

		letterOwnerID = groupLeaderID if game.type == "GROUP" else userID
		newLetters = game.game.switch_player_letters(letterOwnerID)
		if type(newLetters) == bool:
			return await manager.send_direct_message(
				packets.error("Unable to swap tiles right now."),
				userID
			)

		nextTurn = game.mm_next_turn()

		if game.type == "GROUP":
			partnerID = game.get_partner(userID)
			updateCurrentUser = packets.during.game_update({
				"turn": nextTurn,
				"letters": newLetters,
				"partner": partnerID
			})
			await manager.send_direct_message(updateCurrentUser, userID)
			if type(partnerID) != bool:
				updatePartner = packets.during.game_update({
					"turn": nextTurn,
					"letters": newLetters,
					"partner": userID
				})
				await manager.send_direct_message(updatePartner, partnerID)
				otherUsers = [x.userID for x in game.players if x.userID not in [userID, partnerID]]
			else:
				otherUsers = [x.userID for x in game.players if x.userID != userID]
			await manager.broadcast_specific(packets.during.game_update({
				"turn": nextTurn
			}), otherUsers)
		else:
			await manager.broadcast_specific(
				packets.during.game_update({
					"turn": nextTurn
				}),
				[x.userID for x in game.players if x.userID != websocket.user_id] # type: ignore
			)
			await manager.send_direct_message(packets.during.game_update({
				"turn": nextTurn,
				"letters": newLetters
			}), websocket.user_id) # type: ignore

		if game.type == 'BOT' and nextTurn == -2:
			return await GameHandler.bot_turn_handler(game, websocket)
		
		if game.game.finished:
			return await GameHandler.finish_game(websocket)	


	@staticmethod
	async def draft_placed(data: dict, websocket: WebSocket):
		userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
		if type(userConnection) == bool:
			errorPacket = packets.error("You are not authenticated.")
			return await manager.send_message(websocket, json.dumps(errorPacket))

		if userConnection['game'] == None:
			errorPacket = packets.error("You are not in a game")
			return await manager.send_message(websocket, json.dumps(errorPacket))
		
		game = manager.fetch_game(userConnection['game'])
		if type(game) == bool:
			errorPacket = packets.error("You are not in a game")
			return await manager.send_message(websocket, json.dumps(errorPacket))
		
		# get the partner to whoever placed the draftt
		# send the draft to them
		userID = websocket.user_id # type: ignore
		partner = game.get_partner(userID)
		if type(partner) == bool:
			print(f"{userID} has no partner, ignoring the packet.")
			# DONT NEED TO SEND ERROR, THEY JUST DO NOT HAVE A PARTNER
			return
		await manager.send_direct_message(packets.during.draft_placed(data['d']), partner)
	
	@staticmethod
	async def turn_confirmation(data: dict, websocket: WebSocket):
		# pass it off to the game_turn
		userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
		if type(userConnection) == bool:
			errorPacket = packets.error("You are not authenticated.")
			return await manager.send_message(websocket, json.dumps(errorPacket))

		if userConnection['game'] == None:
			errorPacket = packets.error("You are not in a game")
			return await manager.send_message(websocket, json.dumps(errorPacket))
		
		game = manager.fetch_game(userConnection['game'])
		if type(game) == bool:
			errorPacket = packets.error("You are not in a game")
			return await manager.send_message(websocket, json.dumps(errorPacket))
		
		# Check if the pairing's turn
		userID = userConnection['info'].userID
		partnerID = game.get_partner(userID)
		turnAcceptPacket = packets.during.turn_confirmation({
			"name": userConnection['info'].userName 
		})
		await manager.send_direct_message(turnAcceptPacket, partnerID)

		await GameHandler.game_turn(data, websocket)
		
	@staticmethod
	async def turn_decline(data: dict, websocket: WebSocket):
		try:
			# data has nothing.
			userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
			if type(userConnection) == bool:
				errorPacket = packets.error("You are not authenticated.")
				return await manager.send_message(websocket, json.dumps(errorPacket))

			if userConnection['game'] == None:
				errorPacket = packets.error("You are not in a game")
				return await manager.send_message(websocket, json.dumps(errorPacket))
			
			game = manager.fetch_game(userConnection['game'])
			if type(game) == bool:
				errorPacket = packets.error("You are not in a game")
				return await manager.send_message(websocket, json.dumps(errorPacket))
			
			# Check if the pairing's turn
			userID = userConnection['info'].userID
			partnerID = game.get_partner(userID)
			turnDeclinePacket = packets.during.turn_decline({
				"name": userConnection['info'].userName 
			})
			await manager.send_direct_message(turnDeclinePacket, partnerID)
		except Exception as er:
			print(er)
			
	@staticmethod
	async def turn_request(data: dict, websocket: WebSocket):
		try:

			userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
			if type(userConnection) == bool:
				errorPacket = packets.error("You are not authenticated.")
				return await manager.send_message(websocket, json.dumps(errorPacket))

			if userConnection['game'] == None:
				errorPacket = packets.error("You are not in a game")
				return await manager.send_message(websocket, json.dumps(errorPacket))
			
			game = manager.fetch_game(userConnection['game'])
			if type(game) == bool:
				errorPacket = packets.error("You are not in a game")
				return await manager.send_message(websocket, json.dumps(errorPacket))
			
			# Check if the pairing's turn
			userID = userConnection['info'].userID
			
			# Make it check game type == group else just user userID again.
			groupLeaderID = game.get_group_leader_id(userID) if game.type == "GROUP" else userID 
			currentTurn = game.mm_get_current_turn()
			if userID == currentTurn or groupLeaderID == currentTurn:
				

				# get partner id and send suggestion
				# Send the draft to them
				dataDictionary = copy.deepcopy(data['d'])
				dataDictionary['user'] = userID
				sendToPartner = packets.during.turn_request(dataDictionary)
				partnerID = game.get_partner(userID)
				if type(partnerID) == bool:
					# make game turn happen instead
					print("Partner doesnt exist, performing their game turn instead")
					return await GameHandler.game_turn(data, websocket)
				game.game.print_board()
				await manager.send_direct_message(sendToPartner, partnerID)

			else:
				errorPacket = packets.error("It is not your turn currently!")
				return await manager.send_direct_message(errorPacket, websocket.user_id) # type: ignore
				

		except Exception as e:
			print(e)

	@staticmethod
	async def bot_turn_handler(game: Game, websocket: WebSocket):
		await asyncio.sleep(1)
		botPoints = await game.bot_turn()
		newGrid = game.game.export_grid()
		if game.game.finished:
			return await GameHandler.finish_game(websocket)
		nextTurn = game.mm_next_turn()
		# Update the board for other players,
		gameUpdatePacket = packets.during.game_update({
			"grid": newGrid,
			"turn": nextTurn,
		})
		await manager.broadcast_specific(gameUpdatePacket, [x.userID for x in game.players if x.userID != websocket.user_id]) # type: ignore
		# Update the board for the user who just played.
		updateCurrentUser = packets.during.game_update({
			"grid": newGrid,
			"turn": nextTurn,
			"points": botPoints,
			"letters": game.game.fetch_player_letters(websocket.user_id) # type: ignore
		})	
		await manager.send_direct_message(updateCurrentUser, websocket.user_id) # type: ignore
		# check if the bot is next then make the bot play.
		print("NEXT TURN")
		print(nextTurn)
		if game.game.finished:
			return await GameHandler.finish_game(websocket)
		await manager.broadcast_specific(gameUpdatePacket, [x.userID for x in game.players])

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
				errorPacket = packets.error("You are not authenticated.")
				return await manager.send_message(websocket, json.dumps(errorPacket))

			if userConnection['game'] == None:
				errorPacket = packets.error("You are not in a game")
				return await manager.send_message(websocket, json.dumps(errorPacket))
			
			game = manager.fetch_game(userConnection['game'])
			if type(game) == bool:
				errorPacket = packets.error("The game does not exist")
				return await manager.send_message(websocket, json.dumps(errorPacket))
				
			# Check if the pairing's turn
			userID = userConnection['info'].userID
			
			# Make it check game type == group else just user userID again.
			groupLeaderID = game.get_group_leader_id(userID) if game.type == "GROUP" else userID 
			currentTurn = game.mm_get_current_turn()
			if userID == currentTurn or groupLeaderID == currentTurn:
				pointsAmount = await game.game_turn(data['d']['letters'])
				
				if type(pointsAmount) == bool:
					errorPacket = packets.error("Invalid placement of letters!")
					await manager.send_direct_message(errorPacket, websocket.user_id) # type: ignore
					return
					
				newGrid = game.game.export_grid()
				nextTurn = game.mm_next_turn()

				# Update the board for other players,
				gameUpdatePacket = packets.during.game_update({
					"grid": newGrid,
					"turn": nextTurn,
					# Pretty sure if i add this here the way I have implemented it on the frontend will add it to the player.
					"points": pointsAmount
				})
				
				letterOwnerID = None
				if game.type == "GROUP":
					turnPartnersID = game.get_partner(nextTurn)
					# this is the packet that gets sent to everyone, but if the turn if of their leaders, the turn needs to change to them.
					if turnPartnersID != None:
						originalTurn = game.mm_get_current_turn()
						for player in game.players:
							if player.userID == userID:
								continue
							
							if player.userID == turnPartnersID:
								gameUpdatePacket['d']['turn'] = player.userID
							else:
								gameUpdatePacket['d']['turn'] = originalTurn
							await manager.send_direct_message(gameUpdatePacket, player.userID)
							# await manager.broadcast_specific(gameUpdatePacket, [x.userID for x in game.players if x.userID != websocket.user_id]) # type: ignore

					leaderID = game.get_group_leader_id(userID) # type: ignore
					if (leaderID == None):
						print("Leader ID is none...")
						return
					letters = game.game.fetch_player_letters(leaderID)
					partnerID = game.get_partner(userID)
					gameUpdatePacket = packets.during.game_update({
						"grid": newGrid,
						"turn": nextTurn,
						"points": pointsAmount,
						"partner": partnerID,
						"letters": letters
					})
					hasChanged = False
					if leaderID == partnerID and nextTurn == partnerID:
						hasChanged = True
						gameUpdatePacket['d']['turn'] = userID
					# send packet to the person who just send the confirmation
					print(f"Sending user (ID: {userID})\nPacket: {gameUpdatePacket}")
					await manager.send_direct_message(gameUpdatePacket, userID)
					# now gets user's partner
					# if nextturn == userid, change to the partner
					print("partner id: ", partnerID)
					print("user id: ", userID)
					if hasChanged:
						# Changed from nextTurn to userID, so change it back
						gameUpdatePacket['d']['turn'] = nextTurn
					gameUpdatePacket['d']['partner'] = userID
					del gameUpdatePacket['d']['points']
					print(f"Sending partner (ID: {partnerID})\nPacket: {gameUpdatePacket}")
					await manager.send_direct_message(gameUpdatePacket, partnerID)
				else:
					letterOwnerID = userID
					letters = game.game.fetch_player_letters(letterOwnerID) # type: ignore
					updateCurrentUser = packets.during.game_update({
						"grid": newGrid,
						"turn": nextTurn,
						"points": pointsAmount,
						"letters": letters
					})
					await manager.broadcast_specific(gameUpdatePacket, [x.userID for x in game.players if x.userID != websocket.user_id]) # type: ignore
					await manager.send_direct_message(updateCurrentUser, websocket.user_id) # type: ignore
			
				if nextTurn == -2:
					await GameHandler.bot_turn_handler(game, websocket)
				if game.game.finished:
					return await GameHandler.finish_game(websocket)
			else:
				errorPacket = packets.error("It is not your turn currently!")
				return await manager.send_direct_message(errorPacket, websocket.user_id) # type: ignore

		except Exception as e:
			print(e)

	@staticmethod
	async def finish_game(websocket: WebSocket | None = None, game: Game | None = None):
		if game is None:
			if websocket is None:
				return
			userConnection = manager.fetch_connection(websocket.user_id) # type: ignore
			if type(userConnection) == bool:
				return

			if userConnection['game'] == None:
				errorPacket = packets.error("You are not in a game")
				return await manager.send_message(websocket, json.dumps(errorPacket))
			
			game = manager.fetch_game(userConnection['game'])
			if type(game) == bool:
				return
		
		# {
		# 	"grid": grid,
		# 	"players": players,
		# 	"winner": winner,
		# }
		gameResult = game.finish_game()
		
		
	
		async for session in get_session():
			if game.type == "BOT" or game.type == "NORMAL":
				for player in gameResult['players']:
					if player['userID'] != -2:
						resp = await session.execute(select(User).where(User.userID == player['userID']))
						playerObject = resp.scalar_one_or_none()
						if not playerObject:
							print(f"{player['userID']}: This player doesnt exist")
							continue
						if player == gameResult['winner']:
							playerObject.wins+=1 # type: ignore
						else:
							playerObject.loses+=1 # type: ignore
						
						if playerObject.bestScore < player['points']:
							playerObject.bestScore = player['points']
						playerObject.totalScore += player['points']
						playerObject.rank = None
						session.add(playerObject)
				await session.commit()
			else:
				# game type == "GROUP"
				gameResult['groups'] = game.groups
				gameGroups = copy.deepcopy(game.groups)
				leaderIDs = [x[0] for x in gameGroups if len(x) > 0]
				for player in gameResult['players']:
					if player['userID'] in leaderIDs:
						# do them and their partners
						resp = await session.execute(select(User).where(User.userID == player['userID']))
						playerObject = resp.scalar_one_or_none()

						partnerID = game.get_partner(player['userID'])
						partnerObject = None
						if type(partnerID) == int:
							# there is a partner
							resp = await session.execute(select(User).where(User.userID == partnerID))
							partnerObject = resp.scalar_one_or_none()
							

						if player == gameResult['winner']:
							playerObject.wins+=1 # type: ignore
							if partnerObject != None:
								partnerObject.wins+=1 # type: ignore
						else:
							playerObject.loses+=1 # type: ignore
							if partnerObject != None:
								partnerObject.loses+=1 # type: ignore

						if partnerObject != None:
							if partnerObject.bestScore < player['points']:
								partnerObject.bestScore = player['points']

						if playerObject.bestScore < player['points']: # type: ignore
							playerObject.bestScore = player['points'] # type: ignore
						playerObject.totalScore += player['points'] # type: ignore
						
						if partnerObject != None:
							partnerObject.totalScore += player['points']

						session.add(playerObject)
						if partnerObject != None:
							session.add(partnerObject)
				gameResult['partners'] = game.partners
				await session.commit()
		gameFinishPacket = packets.end.game_end(gameResult)
		await manager.broadcast_specific(gameFinishPacket, [x.userID for x in game.players]) # type: ignore
		for player in game.players:
			if player.userID in manager.connections:
				manager.connections[player.userID]['game'] = None
		if game.id in manager.games:
			del manager.games[game.id]
		
	@staticmethod
	async def chat_message(data: dict, websocket: WebSocket):
		userID = websocket.user_id # type: ignore
		userData = manager.connections[userID]['info']
		fetchModel = UserFetch.model_validate(userData)
		connection = manager.fetch_connection(userID)
		if type(connection) == bool:
			print("Person does not exist")
			# TODO: change error code
			await manager.send_message(websocket, json.dumps(packets.start.invalid_game(data['d']['code'])))
			return False
		
		code = connection['game']
		if code == None:
			print("No Game exists")
			# TODO: change error code
			await manager.send_message(websocket, json.dumps(packets.start.invalid_game("")))
			return False
		
		game = manager.fetch_game(code)
		if type(game) == bool:
			print("Game does not exist")
			await manager.send_message(websocket, json.dumps(packets.start.invalid_game(data['d']['code'])))
			# TODO: send error message
			return False
		
		message = data['d']['message']
		print(data['d'])
		toPartner = data['d'].get("partner", False)
		message = profanity_filter(message)
		if toPartner:
			partnerID = game.get_partner(userID)
			if type(partnerID) == int:
				sendPacket = packets.during.chat_message(message, fetchModel, True)
				await manager.broadcast_specific(sendPacket, [partnerID, userID])
			else:
				print("Partner does not exist for the user")
		else:
			sendPacket = packets.during.chat_message(message, fetchModel)
			await manager.broadcast_specific(sendPacket, [x.userID for x in game.players])
		

		
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
				if game.type == "BOT" and websocket.user_id == game.leader and not game.hasStarted: # type: ignore
					await GameHandler.game_start({"d": {"code": game.id}}, websocket)
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
		await asyncio.sleep(.4)
		for player in game.players:
			await GameHandler.game_update(game.id, player.userID)
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

		if game.type == "BOT" and game.hasStarted:
			return await GameHandler.finish_game(game=game)
		
		sendPacket = packets.start.leave_game(game.id, user['info'].model_dump(mode="json"))
		await manager.broadcast_specific(sendPacket, [x.userID for x in game.players if x.userID != userID])
		leavePacket = packets.start.confirm_leave(game.id)
		await manager.send_direct_message(leavePacket, userID)
		try:
			game.remove_player(user['info'])
		except:
			pass
		
		# remove it from the user's dictionary
		manager.connections[userID]['game'] = None

		if len(game.players) == 0:
			if game.id in manager.games:
				del manager.games[game.id]
			return

		if game.hasStarted and game.game.finished:
			return await GameHandler.finish_game(game=game)
		
		# perform game update to show player left.
		for player in game.players:
			print("Sending update to players becauuse of player leave")
			await GameHandler.game_update(game.id, player.userID)
		

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
		if game.hasStarted:
			userID = websocket.user_id if type(websocket) == WebSocket else websocket # type: ignore
			if game.type == "GROUP":
				groupLeaderID = game.get_group_leader_id(userID) # type: ignore
				letters = game.game.fetch_player_letters(groupLeaderID) # type: ignore
				packetData['d']['letters'] = letters # type: ignore
			else:
				packetData['d']['letters'] = game.game.fetch_player_letters(userID) # type: ignore
				
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
				await asyncio.sleep(1)
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
						await GameHandler.player_join(data, websocket)
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
					case "CHAT_MESSAGE":
						await GameHandler.chat_message(data, websocket)
						continue
					# Group based websocket data
					case "DRAFT_PLACED":
						await GameHandler.draft_placed(data, websocket)
						continue
					case "TURN_CONFIRMATION":
						await GameHandler.turn_confirmation(data, websocket)
						continue
					case "TURN_DECLINE":
						await GameHandler.turn_decline(data, websocket)
						continue
					case "TURN_REQUEST":
						await GameHandler.turn_request(data, websocket)
						continue
					case "GAME_END":
						await GameHandler.finish_game(websocket)
						continue
					case "SKIP_TURN":
						await GameHandler.skip_turn(data, websocket)
						continue
					case "SWITCH_TURN":
						await GameHandler.switch_turn(data, websocket)
						continue
			else:	
				return