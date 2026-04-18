from fastapi import APIRouter, Depends, HTTPException
from modules.Authentication import Authentication
from modules.logger import APILogger
from modules.schema import refreshForm, loginForm, registerForm
from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from modules.database.database import get_session
from modules.database.models import User, Token
import os, datetime, secrets, hashlib
from modules.functions import get_current_user

apiLog = APILogger()

router = APIRouter(
	prefix="/auth",
	tags=["auth"],
)

jwtAuthentication = Authentication()

@router.post('/refresh')
async def refresh(refreshData: refreshForm, session: AsyncSession = Depends(get_session)):
	"""
		Refreshes a Bearer Token. This endpoint is used to obtain a new Bearer Token.

		Parameters:
		- `refreshData.token`: The refresh token to be used to obtain a new Bearer Token.

		Returns:
		- `access_token`: The new Bearer Token.
		- `token_type`: The type of the token, which is 'bearer'.
		- `expires_in`: The number of seconds until the token expires.

		Raises:
		- `HTTPException`: If the refresh token is invalid, a 401 status code is returned with the detail 'Invalid refresh token'.
	"""
	apiLog.info(f"/refresh | Received request to refresh token | {refreshData.token[:15]}...")
	resp = await session.execute(select(Token).where(Token.refreshTokenID == refreshData.token))
	tokenData: Token = resp.scalars().first()
	apiLog.info(f"/refresh | Fetching data | {refreshData.token[:15]}...")
	if tokenData:
		apiLog.info(f"/refresh | Granted request, creating new Bearer Token | User ID: {tokenData.userID}")
		accessToken, expiry = jwtAuthentication.create_access_token(tokenData.userID) # type: ignore
		await session.execute(update(Token).where(Token.refreshTokenID == refreshData.token).values(bearerTokenID=accessToken, isActive=True))
		await session.commit()
		apiLog.info(f"/refresh | Committed new Bearer into Database | User ID: {tokenData.userID}")
		return {'access_token': accessToken, 'token_type': 'bearer', 'expires_in': expiry}
	else:
		apiLog.warning(f"/refresh | Invalid Refresh Token, rejected. | {refreshData.token}")
		raise HTTPException(status_code=401, detail="Invalid refresh token")
	
@router.post('/login')
async def login(loginData: loginForm, session: AsyncSession = Depends(get_session)):
	"""
		Login to the system. This endpoint is used to obtain a Bearer Token.

		Parameters:
		- `loginData.username`: The username to be used to login to the system.
		- `loginData.password`: The password to be used to login to the system.

		Returns:
		- `type`: The type of the token, which is 'bearer'.
		- `id`: The ID of the user that the token belongs to.
		- `token`: The Bearer Token.
		- `refresh_token`: The refresh token that can be used to obtain a new Bearer Token.
		- `expires_at`: The number of seconds until the token expires.

		Raises:
		- `HTTPException`: If the password or username is invalid, a 401 status code is returned with the detail 'Incorrect password or username invalid'.
	"""
	resp = await session.execute(select(User).where(User.userName == loginData.username, User.deactivated == False)) # type: ignore 
	user: User = resp.scalars().first() 
	if not user:
		apiLog.warning(f"/login | User not found | {loginData.username}")
		raise HTTPException(status_code=401, detail="Incorrect password or username invalid")

	mysalt = os.getenv('SALT')
	saltedPassword = f'{mysalt}:{loginData.password}'
	hashedPassword = hashlib.sha256(saltedPassword.encode('utf-8')).hexdigest()
	if hashedPassword == (user.userPassword): # pyright: ignore[reportOptionalMemberAccess]
		apiLog.info(f"/login | User found and authenticated | {loginData.username}")
		accessToken, expiry = jwtAuthentication.create_access_token(user.userID) # type: ignore
		apiLog.info(f"/login | Generated Bearer Token | {loginData.username}")
		refresh_token = secrets.token_urlsafe(56)
		apiLog.info(f"/login | Generated Refresh Token | {loginData.username}")

		while True:
			if not (await session.execute(select(Token).where(Token.bearerTokenID == refresh_token))).scalar_one_or_none():
				break
			else:
				refresh_token = secrets.token_urlsafe(56)
				apiLog.info(f"/login | Refresh token regenerated due to duplication. | {loginData.username}")

		refreshTokenObject = Token(refreshTokenID=refresh_token, bearerTokenID=accessToken, userID=user.userID, isActive=True)
		session.add(refreshTokenObject)
		await session.commit()
		apiLog.info(f"/login | Committed new Bearer + Refresh into Database | {loginData.username}")
		return {
			"type": "Bearer",
			"id": user.userID,
			"token": accessToken,
			"refresh_token": refresh_token,
			"expires_at": expiry
		}
	apiLog.warning(f"/login | Incorrect password or username invalid | {loginData.username}")
	raise HTTPException(status_code=401, detail="Incorrect password or username invalid")

@router.post('/register')
async def register(registerData: registerForm, session: AsyncSession = Depends(get_session)):
	resp = await session.execute(select(User).where(User.userName == registerData.username))
	user = resp.scalars().first()
	if user: 
		apiLog.warning(f"/register | User already exists | {registerData.username}")
		raise HTTPException(status_code=404, detail="User already exists")
	
	# check password length
	if len(registerData.password) < 8:
		apiLog.warning(f"/register | Password too short | {registerData.username}")
		raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

	mysalt = os.getenv('SALT')
	saltedPassword = f'{mysalt}:{registerData.password}'
	hashedPassword = hashlib.sha256(saltedPassword.encode('utf-8')).hexdigest()
 
	newUser = User(userName=registerData.username, 
                   userPassword=hashedPassword, 
                   userCreatedAt=datetime.datetime.now(datetime.timezone.utc), 
                   wins=0,
                   loses=0,
                   totalScore=0,
                   bestScore=0)
 
	session.add(newUser)
	await session.commit()
	apiLog.warning(f"/login | Created user and committed. | {registerData.username}")
	return {"message": "User created successfully"}


@router.post('/verifyPassword/@me')
async def verify_password(password: str, current_user: User = Depends(get_current_user)):
    mysalt = os.getenv('SALT')
    saltedPassword = f'{mysalt}:{password}'
    hashedPassword = hashlib.sha256(saltedPassword.encode('utf-8')).hexdigest()
    return hashedPassword == current_user.userPassword


@router.post('/changePassword/@me')
async def change_password(new_password: str, current_user: User = Depends(get_current_user), session: AsyncSession=Depends(get_session)): 
    
    print("Preparing to change password for userID:", current_user.userName)
    
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    

    mysalt = os.getenv('SALT')
    saltedPassword = f'{mysalt}:{new_password}'
    hashedPassword = hashlib.sha256(saltedPassword.encode('utf-8')).hexdigest()
    
    if new_password == current_user.userPassword:
        raise HTTPException(status_code=400, detail="New password cannot be the same as the current password.")
    
    current_user.userPassword = hashedPassword # type: ignore
    session.add(current_user)
    await session.commit()
    return {"detail": "Password changed successfully."}