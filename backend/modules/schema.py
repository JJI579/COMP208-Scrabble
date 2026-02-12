from pydantic import BaseModel
import datetime
from typing import Optional, Literal

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