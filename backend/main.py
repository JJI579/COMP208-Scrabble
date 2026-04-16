from fastapi import FastAPI
from contextlib import asynccontextmanager
from modules.database.database import init_db, close_db, init_db_sync
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path


# For fetching initial words, if not then providing the words to be used.
from modules.database.database import get_session
from modules.database.models import Word
from sqlmodel import select, insert

currentPath = Path.cwd()


@asynccontextmanager
async def lifespan(app: FastAPI):
	init_db_sync()
	await init_db()

	async for session in get_session():
		resp = await session.execute(select(Word).limit(1))
		if resp.scalar_one_or_none() == None:
			# Provide the words from sowpods.txt
			print("Providing the words from sowpods.txt")
			_words = [{'word': x.strip()} for x in open(currentPath / "sowpods.txt", 'r').read().split('\n')]
			await session.execute(insert(Word), _words)
			await session.commit()
		
	yield
	await close_db()

app = FastAPI(title="Scrabble Websocket Application", lifespan=lifespan)

origins = [
	"http://127.0.0.1:5173",
	"http://127.0.0.1",
	"http://localhost:5173",
	"http://localhost:8000",
	"https://w11-desktop.tail57640.ts.net"
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)




@app.get("/")
def serve_vue():
    return {"text": "hello world"}


from routes import auth, users, friends, websocket

from fastapi import APIRouter

router = APIRouter(
	prefix="/api",
	tags=["api"],
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(websocket.router)
app.include_router(websocket.gameRouter)




# app.mount("/assets", StaticFiles(directory="dist/assets", html=True), name="frontend")
