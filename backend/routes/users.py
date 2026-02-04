from fastapi import APIRouter, Depends, HTTPException, Request
from modules.Authentication import Authentication
from modules.logger import APILogger
from modules.schema import refreshForm, loginForm, registerForm
from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from modules.database.database import get_session
from modules.database.models import User, Token
import os, datetime, secrets, hashlib
from modules.functions import get_current_user
from typing import Annotated
apiLog = APILogger()

router = APIRouter(
	prefix="/users",
	tags=["users"],
)

@router.get('/@me')
async def fetch_self(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	return current_user

@router.get('/{user_id}')
async def get_user(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	userID = request.path_params.get('user_id')
	print(userID)
