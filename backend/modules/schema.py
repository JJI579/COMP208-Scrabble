from pydantic import BaseModel
import datetime
from typing import Optional, Literal

PacketType = Literal[
	"CONFIRM_LEAVE",
	"INVALID_GAME",
	"NOT_FOUND",
	"RESUME",
	"IDENTIFY",
	"DISCONNECT",
	"GAME_START",
	"GAME_UPDATE_ONGOING",
	"GAME_CANCEL",
	"PLAYER_JOIN",
	"PLAYER_LEAVE",
	"PLAYER_DISCONNECT",
	"GROUP_UPDATE",
	"GROUP_JOIN",
	"GROUP_LEAVE",
	"GAME_PLACE",
	"GAME_REPLACE",
	"GAME_UPDATE",
	"GAME_TURN",
]

GAME_TYPE = Literal[
	"NORMAL",
	"GROUP",
	"BOT"
]

# Users
class UserFetch(BaseModel):
	userID: int
	userName: str
	userCreatedAt: datetime.datetime

	class Config:
		from_attributes = True

class Tile(BaseModel):
	letter: str
	points: int

class PlacedTile(Tile):
	coordinates: tuple[int, int] 
	
class GamePlayer(UserFetch):
	placed: list[PlacedTile] = []
	points: int = 0

class SelfFetch(UserFetch):
	friends: list[UserFetch]



# Login
class loginForm(BaseModel):
	username: str
	password: str

class registerForm(BaseModel):
	username: str
	password: str

class refreshForm(BaseModel):
	token: str


class GameOptions(BaseModel):
    game_type: GAME_TYPE
    group_size: Optional[int] = None
    time_limit: str
    dictionary: bool

class PersonalItemReturn(BaseModel):
	itemID: int
	name: str
	description: str
	xpRequired: int 
	unlocked: Optional[bool]
	