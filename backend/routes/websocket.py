from fastapi import APIRouter, WebSocket
from fastapi import Depends
from modules.database.database import get_session
from modules.database.database import AsyncSession
from modules.functions import get_current_user
from modules.websocket.WebsocketManager import manager
from modules.logger import WebsocketLogger
router = APIRouter(
	prefix="",
	tags=[],
)

gameRouter = APIRouter(
	prefix="/game",
	tags=["game"],
)

wsLogger = WebsocketLogger();

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	websocket.session_id = secrets.token_hex(40) # type: ignore
	await websocket.accept()
	wsLogger.info(f'New Websocket: {websocket.session_id} | Websocket accepted.') # type: ignore
	userIdentified = False
	while True:
		try:
			data = await websocket.receive_json()
			packetType = data.get('t', '')
			if packetType == "IDENTIFY" and not userIdentified:
				identifyResponse = await manager.identify(websocket, data['d']['token'])
				if not identifyResponse:
					wsLogger.error("Not found, closing websocket.")
					return await websocket.close()
				userIdentified = identifyResponse
				wsLogger.info(f"WS ID: {websocket.session_id} | User Identified: {userIdentified}") # pyright: ignore[reportAttributeAccessIssue]
				websocket.user_id = userIdentified # pyright: ignore[reportAttributeAccessIssue]
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