from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from modules.database.database import Base

class User(Base):
	__tablename__ = "tblUsers"

	userID = Column(Integer, primary_key=True, index=True)
	userName = Column(String, unique=True, nullable=False)
	userPassword = Column(String, nullable=False)
	userCreatedAt = Column(DateTime, default=datetime.utcnow)
	wins = Column(Integer, default=0, nullable=False)
	loses = Column(Integer, default=0, nullable=False)
	totalScore = Column(Integer, default=0, nullable=False)
	bestScore = Column(Integer, default=0, nullable=False)
	deactivated = Column(Boolean, default=False, nullable=False)

class UserConfig(Base):
	__tablename__ = "tblUserConfig"
	userID = Column(Integer, ForeignKey("tblUsers.userID"), primary_key=True, nullable=False)
	itemID = Column(Integer, ForeignKey("tblItems.itemID"), primary_key=True, nullable=False)
	active = Column(Boolean, default=False, nullable=False)
	
class Token(Base):
	__tablename__ = "tblTokens"

	# these are JWT Tokens
	userID = Column(Integer, ForeignKey("tblUsers.userID"), primary_key=True, nullable=False)
	bearerTokenID = Column(String, primary_key=True, nullable=False)
	refreshTokenID = Column(String, primary_key=True, nullable=False)
	createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
	isActive = Column(Boolean, default=True, nullable=False)

class Friend(Base):
	__tablename__ = "tblFriends"
	senderID = Column(Integer, ForeignKey("tblUsers.userID"),  primary_key=True, index=True)
	receiverID = Column(Integer, ForeignKey("tblUsers.userID"), primary_key=True, index=True)
	status = Column(String, index=True)
	createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
	dismissed = Column(Boolean, default=False, nullable=False)

class Game(Base):

	__tablename__ = "tblGames"

	gameID = Column(Integer, primary_key=True, index=True)
	gameCode = Column(String, nullable=False)
	active = Column(Boolean, default=True, nullable=False)
	options = Column(String, nullable=False)

class GamePlayers(Base):

	__tablename__ = "tblGamePlayers"
	
	gameID = Column(Integer, ForeignKey("tblGames.gameID"), primary_key=True, index=True)
	userID = Column(Integer, ForeignKey("tblUsers.userID"), primary_key=True, index=True)
	hasJoined = Column(Boolean, default=False, nullable=False)
	# this is to identify if someone has tried to join but then left!
	hasLeft = Column(Boolean, default=False, nullable=False)

class Word(Base):

	__tablename__ = "tblWords"

	wordID = Column(Integer, primary_key=True, index=True)
	word = Column(String, unique=True, nullable=False)

class Item(Base):

	__tablename__ = "tblItems"

	itemID = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	description = Column(String, nullable=False)
	xpRequired = Column(Integer, nullable=False, default=0)