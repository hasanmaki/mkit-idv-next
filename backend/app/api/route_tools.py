"""API routes for ad-hoc IDV tools."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db_session
from app.models.servers import Servers
from app.models.accounts import Accounts
from app.services.idv.service import IdvService

router = APIRouter()


class ToolRequestBase(BaseModel):
    username: str # This is actually the MSISDN/Account identifier in many contexts

class OtpRequest(ToolRequestBase):
    pin: str

class VerifyOtpRequest(ToolRequestBase):
    otp: str

class TransactionRequest(ToolRequestBase):
    product_id: str
    email: str
    limit_harga: int

class OtpTrxRequest(ToolRequestBase):
    otp: str


async def get_server_and_service(
    session: AsyncSession, username: str
) -> tuple[Servers, IdvService]:
    """Helper to find the server associated with an account (username) and return service."""
    # Logic: Find account by username (msisdn), get its server_id, load server.
    # Note: If account doesn't exist, we might need a default server or error.
    # For now, let's assume the user picks a server or we find one via Account.
    
    # 1. Try to find account
    stmt = select(Accounts).where(Accounts.msisdn == username)
    result = await session.execute(stmt)
    account = result.scalar_one_or_none()

    if not account:
         # Fallback: Get the first active server? Or error?
         # Check if there is ANY server.
         stmt_server = select(Servers).where(Servers.is_active == True).limit(1)
         result_server = await session.execute(stmt_server)
         server = result_server.scalar_one_or_none()
         if not server:
            raise HTTPException(status_code=404, detail="No active server found and account not registered.")
    else:
        # Get server from account
        stmt_server = select(Servers).where(Servers.id == account.server_id)
        result_server = await session.execute(stmt_server)
        server = result_server.scalar_one_or_none()
        if not server:
             raise HTTPException(status_code=404, detail="Server for this account not found.")

    return server, IdvService.from_server(server)


@router.post("/otp/request")
async def request_otp(
    payload: OtpRequest,
    session: AsyncSession = Depends(get_db_session),
):
    _, service = await get_server_and_service(session, payload.username)
    return await service.request_otp(payload.username, payload.pin)


@router.post("/otp/verify")
async def verify_otp(
    payload: VerifyOtpRequest,
    session: AsyncSession = Depends(get_db_session),
):
    _, service = await get_server_and_service(session, payload.username)
    return await service.verify_otp(payload.username, payload.otp)


@router.post("/balance")
async def get_balance(
    payload: ToolRequestBase,
    session: AsyncSession = Depends(get_db_session),
):
    _, service = await get_server_and_service(session, payload.username)
    return await service.get_balance_pulsa(payload.username)


@router.post("/products")
async def list_products(
    payload: ToolRequestBase,
    session: AsyncSession = Depends(get_db_session),
):
    _, service = await get_server_and_service(session, payload.username)
    return await service.list_produk(payload.username)


@router.post("/token")
async def get_token(
    payload: ToolRequestBase,
    session: AsyncSession = Depends(get_db_session),
):
    _, service = await get_server_and_service(session, payload.username)
    return await service.get_token_location3(payload.username)


@router.post("/trx")
async def trx_voucher(
    payload: TransactionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    _, service = await get_server_and_service(session, payload.username)
    return await service.trx_voucher_idv(
        payload.username, payload.product_id, payload.email, payload.limit_harga
    )

@router.post("/trx/otp")
async def otp_trx(
    payload: OtpTrxRequest,
    session: AsyncSession = Depends(get_db_session),
):
    _, service = await get_server_and_service(session, payload.username)
    return await service.otp_trx(payload.username, payload.otp)
