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
	return current_user

@router.get('/{user_id}')
async def get_user(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	userID = request.path_params.get('user_id')
	print(userID)



	
