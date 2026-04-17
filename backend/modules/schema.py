from pydantic import BaseModel, Field
import datetime
from typing import Optional, Literal

PacketType = Literal[
	"GAME_END",
	"CHAT_MESSAGE",
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
	"DRAFT_PLACED",
	"DRAFT_REMOVED",
	"TURN_CONFIRMATION",
	"TURN_DECLINE",
	"TURN_REQUEST"
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
	wins: int
	loses: int
	totalScore: int
	bestScore: int
	rank: int | None = None

	class Config:
		from_attributes = True

class Tile(BaseModel):
	letter: str
	points: int

class PlacedTile(Tile):
	coordinates: tuple[int, int] 
	
class GamePlayer(UserFetch):
	placed: list[PlacedTile] = Field(default_factory=list)
	points: int = 0

	def __str__(self) -> str:
		return str(self.dump_json())

	def dump_json(self):
		return {
			"userID": self.userID,
			"userName": self.userName,
			"userCreatedAt": self.userCreatedAt,
			"placed": self.placed,
			"points": self.points
		}

class BotPlayer(BaseModel):
	userID: int = -2
	userName: str = "Bot"
	bot: bool = True
	placed: list[PlacedTile] = Field(default_factory=list)
	points: int = 0

	def dump_json(self):
		return {
			"userID": self.userID,
			"userName": self.userName,
			"bot": self.bot,
			"placed": self.placed,
			"points": self.points
		}
	

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
 
 
#  Friends
class FriendRequest(BaseModel):
    toUserID: int
    

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
	
