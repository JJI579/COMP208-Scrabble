from fastapi import APIRouter, WebSocket
from fastapi import Depends
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
	print(options.game_type)
	print(options.time_limit)
	print(options.dictionary)
	print(options.group_size)
	CODE = manager.create_game(options)
	return {
		"code": CODE
	}

wsLogger = WebsocketLogger();

from modules.websocket.packets import packets
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
	print("Websocket found")
	websocket.session_id = secrets.token_hex(40) # type: ignore
	await websocket.accept()
	wsLogger.info(f'New Websocket: {websocket.session_id} | Websocket accepted.') # type: ignore
	userIdentified = False
	while True:
		try:
			data = await websocket.receive_json()
			packetType: PacketType = data.get('t', '')
			print("PACKET TYPE: ", packetType)
			if packetType == "IDENTIFY" and not userIdentified:
				identifyResponse = await manager.identify(websocket, data['d']['token'])
				if not identifyResponse:
					wsLogger.error("Not found, closing websocket.")
					return await websocket.close()
				userIdentified = identifyResponse
				wsLogger.info(f"WS ID: {websocket.session_id} | User Identified: {userIdentified}") # pyright: ignore[reportAttributeAccessIssue]
				websocket.user_id = userIdentified # pyright: ignore[reportAttributeAccessIssue]
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
								break
							try:
								game.add_player(userIdentified)
								resp = await session.execute(select(User).where(User.userID == websocket.user_id)) # type: ignore
								userObj = resp.scalar_one()
								thePacket = packets.start.join_game(gameCode, UserFetch.model_validate(userObj).model_dump())
								print(thePacket)
								# TODO: broadcast "thePacket" to game players apart from the one who joined
							except Exception as er:
								wsLogger.error(f"WS ID: {websocket.session_id} | Error: {er}") # pyright: ignore[reportAttributeAccessIssue]
								# TODO: send error packet.
								break
							


				else:
					wsLogger.info(f"Closing Websocket: {websocket.session_id} | Attempted to send data when Unauthenticated") # pyright: ignore[reportAttributeAccessIssue]
					await websocket.close()
		except Exception as e:
			wsLogger.error(f"{websocket.session_id} | Error: {e}") # type: ignore
			try:
				potentialID	 = getattr(websocket, "user_id")
				if potentialID:
					wsLogger.info(f"WS ID: {websocket.session_id} | Removed from active connections: {potentialID}") # type: ignore
					await manager.remove(potentialID)
			except AttributeError:
				break
			break