"""API routes for ad-hoc IDV tools."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.models.accounts import Accounts
from app.models.bindings import Bindings
from app.models.servers import Servers
from app.services.idv.service import IdvService

router = APIRouter()


class ToolRequestBase(BaseModel):
    """Base ad-hoc request payload identified by username/msisdn."""

    username: str
    server_id: int | None = None
    batch_id: str | None = None


class OtpRequest(ToolRequestBase):
    """Request payload for OTP request."""

    pin: str


class VerifyOtpRequest(ToolRequestBase):
    """Request payload for OTP verification."""

    otp: str


class TransactionRequest(ToolRequestBase):
    """Request payload for transaction initiation."""

    product_id: str
    email: str
    limit_harga: int


class OtpTrxRequest(ToolRequestBase):
    """Request payload for transaction OTP submission."""

    otp: str


async def get_server_and_service(
    session: AsyncSession,
    username: str,
    *,
    server_id: int | None = None,
    batch_id: str | None = None,
) -> tuple[Servers, IdvService]:
    """Resolve server for ad-hoc tool call from explicit server or active binding."""
    if server_id is not None:
        stmt_server = select(Servers).where(
            and_(Servers.id == server_id, Servers.is_active.is_(True))
        )
        result_server = await session.execute(stmt_server)
        server = result_server.scalar_one_or_none()
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Server aktif dengan id={server_id} tidak ditemukan.",
            )
        return server, IdvService.from_server(server)

    stmt = select(Accounts).where(Accounts.msisdn == username)
    if batch_id:
        stmt = stmt.where(Accounts.batch_id == batch_id)
    result = await session.execute(stmt)
    accounts = result.scalars().all()

    if len(accounts) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MSISDN ditemukan di beberapa batch. Sertakan batch_id.",
        )

    account = accounts[0] if accounts else None
    if account is not None:
        stmt_binding = (
            select(Bindings)
            .where(
                and_(
                    Bindings.account_id == account.id,
                    Bindings.unbound_at.is_(None),
                )
            )
            .order_by(Bindings.id.desc())
        )
        result_binding = await session.execute(stmt_binding)
        binding = result_binding.scalars().first()
        if binding is not None:
            stmt_server = select(Servers).where(
                and_(Servers.id == binding.server_id, Servers.is_active.is_(True))
            )
            result_server = await session.execute(stmt_server)
            server = result_server.scalar_one_or_none()
            if server is not None:
                return server, IdvService.from_server(server)

    stmt_server = (
        select(Servers).where(Servers.is_active.is_(True)).order_by(Servers.id).limit(1)
    )
    result_server = await session.execute(stmt_server)
    server = result_server.scalar_one_or_none()
    if server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tidak ada server aktif yang tersedia.",
        )

    return server, IdvService.from_server(server)


@router.post("/otp/request")
async def request_otp(
    payload: OtpRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Request OTP to provider."""
    _, service = await get_server_and_service(
        session,
        payload.username,
        server_id=payload.server_id,
        batch_id=payload.batch_id,
    )
    return await service.request_otp(payload.username, payload.pin)


@router.post("/otp/verify")
async def verify_otp(
    payload: VerifyOtpRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Verify OTP to provider."""
    _, service = await get_server_and_service(
        session,
        payload.username,
        server_id=payload.server_id,
        batch_id=payload.batch_id,
    )
    return await service.verify_otp(payload.username, payload.otp)


@router.post("/balance")
async def get_balance(
    payload: ToolRequestBase,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch pulsa balance from provider."""
    _, service = await get_server_and_service(
        session,
        payload.username,
        server_id=payload.server_id,
        batch_id=payload.batch_id,
    )
    return await service.get_balance_pulsa(payload.username)


@router.post("/products")
async def list_products(
    payload: ToolRequestBase,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch product list from provider."""
    _, service = await get_server_and_service(
        session,
        payload.username,
        server_id=payload.server_id,
        batch_id=payload.batch_id,
    )
    return await service.list_produk(payload.username)


@router.post("/token")
async def get_token(
    payload: ToolRequestBase,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch token location from provider."""
    _, service = await get_server_and_service(
        session,
        payload.username,
        server_id=payload.server_id,
        batch_id=payload.batch_id,
    )
    return await service.get_token_location3(payload.username)


@router.post("/trx")
async def trx_voucher(
    payload: TransactionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Create voucher transaction to provider."""
    _, service = await get_server_and_service(
        session,
        payload.username,
        server_id=payload.server_id,
        batch_id=payload.batch_id,
    )
    return await service.trx_voucher_idv(
        payload.username, payload.product_id, payload.email, payload.limit_harga
    )

@router.post("/trx/otp")
async def otp_trx(
    payload: OtpTrxRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Submit OTP for provider transaction."""
    _, service = await get_server_and_service(
        session,
        payload.username,
        server_id=payload.server_id,
        batch_id=payload.batch_id,
    )
    return await service.otp_trx(payload.username, payload.otp)
