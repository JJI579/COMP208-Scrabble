from modules.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from typing import TypedDict, Annotated
from modules.Authentication import Authentication
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from modules.database.models import User, Token

JWTToken = TypedDict('JWTToken', {
	"type": str,
	"id": int,
	"exp": float
})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
jwtAuthentication = Authentication()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(get_session)):
	# Get current user based on their bearer token they provide.
	credentialsException = HTTPException(status_code=401, detail="Invalid or expired Bearer Token")
	try:
		decodedToken: JWTToken = jwtAuthentication.decode_access_token(token) # type: ignore
	except:
		raise credentialsException

	resp = await session.execute(select(Token, User).where(Token.bearerTokenID == token).join(User, User.userID == decodedToken['id']))
	result = resp.all()
	if not result:
		raise credentialsException
	return result[0][1]