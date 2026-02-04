from pydantic import BaseModel
import datetime
from typing import Optional
class PhotoCreate(BaseModel):
	photoName: str
	photoType: str
	photoData: str
	photoCaption: str = ""

class UserFetch(BaseModel):
	userID: int
	userName: str
	userCreatedAt: datetime.datetime

	class Config:
		from_attributes = True


class SelfFetch(UserFetch):
	friends: list[UserFetch]

class CommentCreate(BaseModel):
	comment: str

class loginForm(BaseModel):
	username: str
	password: str

class registerForm(BaseModel):
	username: str
	password: str

class refreshForm(BaseModel):
	token: str

class TokenForm(BaseModel):
	token: str
	platform: str