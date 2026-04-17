from fastapi import APIRouter, Depends, HTTPException, Request
from modules.Authentication import Authentication
from modules.logger import APILogger
from modules.schema import refreshForm, loginForm, registerForm
from sqlmodel import select, delete, and_, or_, join
from sqlalchemy.ext.asyncio import AsyncSession
from modules.database.database import get_session
from modules.database.models import User, Friend
import os, datetime, secrets, hashlib
from modules.functions import get_current_user
from typing import Annotated
apiLog = APILogger()
from modules.schema import UserFetch, FriendRequest


router = APIRouter(
    prefix="/friends",
    tags=["friends"]
)

@router.post('/request')
async def send_friend_request(data: FriendRequest, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    receivedID = data.toUserID
    senderID = current_user.userID
    
    if receivedID == senderID:
        raise HTTPException(status_code=400, detail="You cannot send a request to yourself!!!")
    
    if receivedID is None or senderID is None:
        raise HTTPException(status_code=400, detail="Invalid user ID(-s)!!!")
    
    res = await session.execute(select(User).where(User.userID == receivedID))
    if not res.scalar():
        raise HTTPException(status_code=404, detail="The user youre sending the request to doesnt exist!!")
    
    res = await session.execute(select(Friend).where(and_(Friend.senderID == senderID, Friend.receiverID == int(receivedID))))
    result = res.scalar_one_or_none()
    if result:
        result: Friend
        if result.status == "cancelled": # type: ignore
            result.status = "pending" # type: ignore
            await session.commit()
            return {"message": "Friend request has been successfully sent!!"}
        raise HTTPException(status_code=400, detail="You have already sent a request to this user!!")
    else:
        session.add(Friend(senderID = senderID, receiverID = receivedID, status = "pending"))
        await session.commit()
        return {"message": "The friend request has been successfully sent!"}
    
    
@router.get('/myFriends', response_model = list[UserFetch])
async def get_friends(current_user: Annotated[User, Depends(get_current_user)], limit: int = 1000, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(User).distinct()
        .join(
            Friend,
            or_(
                (Friend.senderID == current_user.userID) & (Friend.receiverID == User.userID),
                (Friend.receiverID == current_user.userID) & (Friend.senderID == User.userID)
            )
        )
        .where(
            Friend.status == "accepted",
            User.userID != current_user.userID
        ).limit(limit)
    )
    
    results = res.scalars().all()
    return results
    
    
@router.post('/accept')
async def accept_friend_request(data: FriendRequest, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    receiverID = current_user.userID
    senderID = data.toUserID
    if receiverID is None or senderID is None:
        raise HTTPException(status_code=400, detail="Invalid user ID(-s)!!")
    
    res = await session.execute(select(Friend).where(
        and_(
            Friend.senderID == senderID,
            Friend.receiverID == receiverID,
            Friend.status == "pending"
        )
    ))
    result = res.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="No pending friend request from this user!!")
    result.status = "accepted" # type: ignore
    await session.commit()
    print("Friend request accepted!!")
    return {"message": "Friend request has been accepted!!"}


@router.post('/decline')
async def decline_friend_request(data: FriendRequest, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    receiverID = current_user.userID
    senderID = data.toUserID
    
    if receiverID is None or senderID is None:
        raise HTTPException(status_code=400, detail="Invalid user ID(-s)!!")
    
    res = await session.execute(delete(Friend).where(
        and_(
            Friend.senderID == senderID,
            Friend.receiverID == receiverID,
            Friend.status == "pending"
        )
    ))
    
    await session.commit()
    print("Friend request has been declined")
    
         
@router.get('/requests', response_model = list[UserFetch])
async def get_friend_requests(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    search = await session.execute(select(Friend.senderID).where(and_(Friend.receiverID == current_user.userID, Friend.status == "pending")))
    search = search.scalars().all()
    res = await session.execute(select(User).where(User.userID.in_(search)))
    requests = res.scalars().all()
    return requests

@router.get('/sent')
async def get_sent_requests(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    search = await session.execute(select(Friend.receiverID).where(and_(Friend.senderID == current_user.userID, Friend.status == "pending")))
    search = search.scalars().all()
    res = await session.execute(select(User.userID).where(User.userID.in_(search)))
    requests = res.scalars().all()
    return requests