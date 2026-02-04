from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from modules.database.database import Base

class User(Base):
	__tablename__ = "tblUsers"

	userID = Column(Integer, primary_key=True, index=True)
	userName = Column(String, unique=True, nullable=False)
	userPassword = Column(String, nullable=False)
	userCreatedAt = Column(DateTime, default=datetime.utcnow)
	deactivated = Column(Boolean, default=False, nullable=False)

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






