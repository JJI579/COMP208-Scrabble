from fastapi import APIRouter, Depends, HTTPException
from modules.logger import APILogger
from sqlalchemy.ext.asyncio import AsyncSession
from modules.database.database import get_session
from modules.database.models import User, Item, UserConfig
from typing import Annotated
from modules.functions import get_current_user
from sqlmodel import select, case
from modules.schema import PersonalItemReturn
from sqlalchemy import and_
apiLog = APILogger()

router = APIRouter(
	prefix="/auth",
	tags=["auth"],
)


@router.get('/fetch')
async def fetch_items(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)) -> list[PersonalItemReturn]:
    resp = await session.execute(select(Item).order_by(Item.xpRequired.asc()))
    stmt = select(
        Item,
        case(
            (current_user.xpGained >= Item.xpRequired, True),
            else_=False
        ).label("unlocked")
    ).order_by(Item.xpRequired)
    resp = await session.execute(stmt)
    items = []
    for item, unlocked in resp.scalars().all():
        newItem = PersonalItemReturn.model_validate(item)
        newItem.unlocked = unlocked
        items.append(newItem)
    return items




@router.post('/{item_id}/equip')
async def equip_item(item_id: int, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    resp = await session.execute(select(Item).where(Item.itemID == item_id))
    item = resp.scalar_one_or_none()
    if item == None:
        raise HTTPException(status_code=404, detail="Not found")
    
    configResp = await session.execute(select(UserConfig).where(and_(
        UserConfig.userID == current_user.userID,
        UserConfig.itemID == item.itemID
    )))
    config = configResp.scalar_one_or_none()
    if config == None:
        # Create new config for item
        obj = UserConfig(userID=current_user.userID, itemID=item.itemID, active=1)
        session.add(obj)
    else:
        config.active = 1 # type: ignore
    await session.commit()


@router.post('/{item_id}/unequip')
async def unequip_item(item_id: int, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    resp = await session.execute(select(Item).where(Item.itemID == item_id))
    item = resp.scalar_one_or_none()
    if item == None:
        raise HTTPException(status_code=404, detail="Not found")
    
    configResp = await session.execute(select(UserConfig).where(and_(
        UserConfig.userID == current_user.userID,
        UserConfig.itemID == item.itemID
    )))
    config = configResp.scalar_one_or_none()
    if config == None:
        # Create new config for item
        obj = UserConfig(userID=current_user.userID, itemID=item.itemID, active=0)
        session.add(obj)
    else:
        config.active = 0 # type: ignore
    await session.commit()

