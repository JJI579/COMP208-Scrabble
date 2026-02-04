from pydantic import BaseModel
import datetime

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