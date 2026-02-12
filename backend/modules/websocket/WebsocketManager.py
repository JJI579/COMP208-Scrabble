from fastapi import APIRouter, WebSocket
from fastapi import Depends
from modules.database.database import get_session
from modules.database.database import AsyncSession

router = APIRouter(
	prefix="/",
	tags=[""],
)


@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
	pass