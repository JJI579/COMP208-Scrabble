from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.modules.database.database import init_db, close_db, init_db_sync, get_session
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

currentPath = Path.cwd()


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

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/")
async def root():
	return {"message": "Hello World"}


from routes import auth, users, friends, websocket

app.include_router(websocket.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(websocket.router)
app.include_router(websocket.gameRouter)
