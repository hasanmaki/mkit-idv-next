from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.services.servers import ServerCreate, ServerResponse, ServerService

router = APIRouter()


@router.post("/", response_model=ServerResponse)
async def create_server(
    payload: ServerCreate,
    session: AsyncSession = Depends(get_db_session),
):
    service = ServerService(session)
    return await service.create_server(payload)
