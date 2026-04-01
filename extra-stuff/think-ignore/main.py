from fastapi import FastAPI, WebSocket, Depends
from contextlib import asynccontextmanager
from modules.database import init_db, close_db, init_db_sync, get_session
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import secrets
currentPath = Path.cwd()
from modules.WebsocketManager import manager
from modules.logger import WebsocketLogger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
wsLogger = WebsocketLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
	init_db_sync()
	await init_db()
	yield
	await close_db()

app = FastAPI(title="Scrabble Websocket Application", lifespan=lifespan)

origins = [
	"http://127.0.0.1:5173",
	"http://localhost:5173"
]


# this is great
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,      # explicit allowed origins
	allow_credentials=True,     # allow cookies or Authorization headers
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/")
async def root():
	return {"message": "Hello World"}



class tempForm(BaseModel):
	string: str



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
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
			