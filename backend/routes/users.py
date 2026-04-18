from fastapi import APIRouter, Depends, Request
from modules.logger import APILogger
from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from modules.database.database import get_session
from modules.database.models import User, UserConfig
from modules.functions import get_current_user
from typing import Annotated
apiLog = APILogger()
from modules.schema import UserFetch, SelfFetch

from sqlalchemy import insert

router = APIRouter(
	prefix="/users",
	tags=["users"],
)

@router.get('/@me')
async def fetch_self(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)) -> SelfFetch:
	result = await session.execute(select(User).order_by(User.totalScore.desc()))
	users = result.scalars().all()
	
	rank = next((i + 1 for i, user in enumerate(users) if (user.userID == current_user.userID)), None) # type: ignore
	
	SelfFetchModel = SelfFetch.model_validate(current_user)
	SelfFetchModel.rank = rank

	resp = await session.execute(select(UserConfig).where(UserConfig.userID == current_user.userID))
	SelfFetchModel.config = {x.itemID:x.active for x in resp.scalars().all()}
	
	return SelfFetchModel
	

@router.get('/players', response_model = list[UserFetch])
async def get_users(search: str = '', session: AsyncSession = Depends(get_session)):
	if (search == ''):
		return []
	query = user_search(select(User), search)
	results = await session.execute(query.order_by(User.userName.asc().where(User.deactivated == False))) # type: ignore
	users = results.scalars().all()
	return users

@router.get('/leaderboard', response_model=list[UserFetch])
async def get_leaderboard(sort_by: str = "totalScore", search: str = '', limit: int = 100, session: AsyncSession = Depends(get_session)):
	if sort_by == "totalScore":
		order_by = User.totalScore
	elif sort_by == "wins":
		order_by = User.wins
	elif sort_by == "games":
		order_by = User.wins + User.loses
	else:
		order_by = User.bestScore
		
	query = user_search(select(User), search).where(User.deactivated == False) # type: ignore
	query = query.order_by(order_by.desc()).limit(limit)
	
	results = await session.execute(query)
	users = results.scalars().all()
	return users


@router.get('/{user_id}')
async def get_user(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	userID = request.path_params.get('user_id')
	print(userID)
 

@router.post('/changeUsername/@me')
async def change_username(new_username: str, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
    
    print("changing the name")
    print(new_username)
    
    resp = await session.execute(select(User).where(User.userName == new_username))
    our_user: User = resp.scalars().first()
    if our_user:
        raise HTTPException(status_code=400, detail="Username already taken.")
    
    if new_username == current_user.userName:
        raise HTTPException(status_code=400, detail="New username cannot be the same as the current username.")
    
    print("Changing username for userID:", current_user.userID, "to new username:", new_username)
    
    current_user.userName = new_username # type: ignore
    session.add(current_user)
    await session.commit()
    return {"detail": "Username changed successfully."}
 

@router.delete('/delete/@me')
async def delete_self(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
    setattr(current_user, 'deactivated', True)
    session.add(current_user)
    await session.commit()
    return {"detail": "Account deactivated successfully."}
 
 

def user_search(query, name: str):
	if name:
		return query.where(User.userName.ilike(f"%{name}%"))
	return query

