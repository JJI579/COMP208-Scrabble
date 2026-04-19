from fastapi import APIRouter, Depends, HTTPException
from modules.logger import APILogger
from sqlalchemy.ext.asyncio import AsyncSession
from modules.database.database import get_session
from modules.database.models import User, Item, UserConfig
from typing import Annotated, cast
from modules.functions import get_current_user
from sqlmodel import select, case
from modules.schema import PersonalItemReturn
from sqlalchemy import and_
import json
apiLog = APILogger()

router = APIRouter(
	prefix="/items",
	tags=["items"],
)


@router.get('/fetch')
async def fetch_items(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)) -> list[PersonalItemReturn]:
    resp = await session.execute(select(Item).order_by(Item.xpRequired.asc()))
    all_items = resp.scalars().all()
    
    configResp = await session.execute(select(UserConfig).where(UserConfig.userID == current_user.userID))
    userConfigs = configResp.scalars().all()
    
    configMap = {config.itemID: config.active for config in userConfigs}
    
    items = []
    
    for item in all_items:
        newItem = PersonalItemReturn.model_validate(item)
        newItem.unlocked = bool(current_user.totalScore >= item.xpRequired)
        newItem.equipped = bool(configMap.get(item.itemID, False))
        items.append(newItem)
        
    return items
        


@router.post('/{item_id}/equip')
async def equip_item(item_id: int, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    resp = await session.execute(select(Item).where(Item.itemID == item_id))
    item = resp.scalar_one_or_none()
    if item == None:
        raise HTTPException(status_code=404, detail="Not found")
    
    userScore = cast(int, current_user.totalScore)
    requiredScore = cast(int, item.xpRequired)
    
    
    if userScore < requiredScore:
        raise HTTPException(status_code=403, detail="Not unlocked")
    
    configResp = await session.execute(select(UserConfig).where(and_(
        UserConfig.userID == current_user.userID,
        UserConfig.itemID == item.itemID
    )))
    config = configResp.scalar_one_or_none()
    
    if not config:
        config = UserConfig(userID = current_user.userID,
                         itemID = item.itemID,
                         active = 0)
        session.add(config)
        
    sameCategoryResp = await session.execute(select(UserConfig).join(
        Item, Item.itemID == UserConfig.itemID).where(and_(
            UserConfig.userID == current_user.userID,
            Item.category == item.category
        ))
    )
    sameCategoryConfigs = sameCategoryResp.scalars().all()
    
    for row in sameCategoryConfigs:
        row.active = 0 #type: ignore
    
    config.active = 1 #type: ignore
    await session.commit()
    
    print("You have equipped the item: " + item.name)
    
    return {
        "message": "Item equipped successfully"
    }



@router.post('/{item_id}/unequip')
async def unequip_item(item_id: int, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    resp = await session.execute(select(UserConfig).where(and_(
        UserConfig.itemID == item_id,
        UserConfig.userID == current_user.userID
    )))
    
    config = resp.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail='Item not equipped')
    
    config.active = 0 #type: ignore
    await session.commit()
    
    return {
        "message" : "Item unequipped successfully"
    }

