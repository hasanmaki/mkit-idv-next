"""API dependencies - centralized dependency injection.

Provides reusable dependency functions for API routes.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.services.accounts.service import AccountService
from app.services.bindings.service import BindingService
from app.services.orders.service import OrderService
from app.services.servers.service import ServerService


def get_server_service(
    session: AsyncSession = Depends(get_db_session),
) -> ServerService:
    """Get server service instance.

    Usage:
        service: ServerService = Depends(get_server_service)
    """
    return ServerService(session)


def get_order_service(
    session: AsyncSession = Depends(get_db_session),
) -> OrderService:
    """Get order service instance.

    Usage:
        service: OrderService = Depends(get_order_service)
    """
    return OrderService(session)


def get_binding_service(
    session: AsyncSession = Depends(get_db_session),
) -> BindingService:
    """Get binding service instance.

    Usage:
        service: BindingService = Depends(get_binding_service)
    """
    return BindingService(session)


def get_account_service(
    session: AsyncSession = Depends(get_db_session),
) -> AccountService:
    """Get account service instance.

    Usage:
        service: AccountService = Depends(get_account_service)
    """
    return AccountService(session)
