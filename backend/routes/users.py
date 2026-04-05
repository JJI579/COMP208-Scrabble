from fastapi import APIRouter, Depends, HTTPException, Request
from modules.Authentication import Authentication
from modules.logger import APILogger
from modules.schema import refreshForm, loginForm, registerForm
from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from modules.database.database import get_session
from modules.database.models import User, Token, Word
import os, datetime, secrets, hashlib
from modules.functions import get_current_user
from typing import Annotated
apiLog = APILogger()
from modules.schema import UserFetch 

from sqlalchemy import insert

router = APIRouter(
	prefix="/users",
	tags=["users"],
)

# when we need to append words.
# @router.get('/words')
# async def putWords(session: AsyncSession = Depends(get_session)):
# 	_words = [{'word': x.strip()} for x in open('sowpods.txt', 'r').read().split('\n')]
# 	total = 0

# 	await session.execute(insert(Word), _words)
# 	await session.commit()
	
# 	return {'total': len(_words)}

@router.get('/@me', response_model=UserFetch)
async def fetch_self(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).order_by(User.totalScore.desc()))
    users = result.scalars().all()
    
    rank = next((i + 1 for i, user in enumerate(users) if (user.userID == current_user.userID)), None) # type: ignore
    print(rank)
    
    return {
        **current_user.__dict__,
        "rank": rank
    }
    
    


@router.get('/leaderboard', response_model=list[UserFetch])
async def get_leaderboard(sort_by: str = "totalScore", search: str = '', limit: int = 100, session: AsyncSession = Depends(get_session)):
    
    print(limit)

    if sort_by == "totalScore":
        order_by = User.totalScore
        print("sorting by totalScore")
    elif sort_by == "wins":
        order_by = User.wins
        print("sorting by wins")
    elif sort_by == "games":
        order_by = User.wins + User.loses
        print("sorting by games")
    else:
        order_by = User.bestScore
        
    query = user_search(select(User), search)
    query = query.order_by(order_by.desc()).limit(limit)
    
    results = await session.execute(query)
    users = results.scalars().all()
    print(users)
    return users


@router.get('/{user_id}')
async def get_user(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	userID = request.path_params.get('user_id')
	print(userID)
 
 

def user_search(query, name: str):
    if name:
        return query.where(User.userName.ilike(f"%{name}%"))
    return query

