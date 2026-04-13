from fastapi import APIRouter, Depends
from modules.logger import APILogger
from sqlalchemy.ext.asyncio import AsyncSession
from modules.database.database import get_session
from modules.database.models import User, Item
from typing import Annotated
from modules.functions import get_current_user
from sqlmodel import select
apiLog = APILogger()

router = APIRouter(
	prefix="/auth",
	tags=["auth"],
)


@router.get('/fetch')
async def fetch_items(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)) -> list[Item]:
    resp = await session.execute(select(Item).order_by(Item.xpRequired.asc()))
    
    return list(resp.scalars().all())