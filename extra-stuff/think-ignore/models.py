from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from modules.database import Base

class Game(Base):
	__tablename__ = "tblGames"

	gameID = Column(Integer, primary_key=True, index=True)
	ownerID = Column(Integer, primary_key=True, index=True)
	createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
	# If a game is created it is assumed to be ongoing
	isOngoing = Column(Boolean, default=True, nullable=False)
	lastMove = Column(DateTime, default=datetime.utcnow, nullable=False)


class User(Base):
	__tablename__ = "tblUsers"

	userID = Column(Integer, primary_key=True, index=True)
	username = Column(String, nullable=False)
	email = Column(String, nullable=False)
	password = Column(String, nullable=False)
	createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

class Session(Base):
	# used as websocket identifier
	__tablename__ = "tblSessions"

	sessionID = Column(String, primary_key=True, index=True)
	userID = Column(Integer, ForeignKey("tblUsers.userID"), nullable=False)
	createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

class UserGames(Base):
	__tablename__ = "tblUserGames"

	userID = Column(Integer, ForeignKey("tblUsers.userID"), primary_key=True, index=True)
	gameID = Column(Integer, ForeignKey("tblGames.gameID"), primary_key=True, index=True)

