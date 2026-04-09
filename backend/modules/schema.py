from pydantic import BaseModel
import datetime

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
    