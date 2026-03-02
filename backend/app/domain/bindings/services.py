"""Binding domain service for domain-level business logic."""

from typing import Protocol

from app.domain.bindings.entities import Binding
from app.domain.bindings.exceptions import AccountAlreadyBoundError, BindingNotFoundError


class BindingRepositoryProtocol(Protocol):
    """Protocol for binding repository (dependency inversion)."""

    async def get(self, session: object, binding_id: int) -> Binding | None:
        """Get binding by ID."""
        ...

    async def get_by_account(self, session: object, account_id: int) -> Binding | None:
        """Get binding by account ID."""
        ...

    async def create(self, session: object, **kwargs) -> Binding:
        """Create a new binding."""
        ...

    async def update(self, session: object, binding: Binding, **kwargs) -> Binding:
        """Update a binding."""
        ...


class BindingDomainService:
    """Domain service for binding operations.

    Contains business logic that doesn't naturally fit within a single entity.
    """

    def __init__(self, repository: BindingRepositoryProtocol | None = None):
        self.repository = repository

    async def validate_account_not_bound(
        self,
        account_id: int,
        exclude_binding_id: int | None = None,
    ) -> None:
        """Validate that an account is not already bound.

        Raises AccountAlreadyBoundError if account is already bound.
        """
        if not self.repository:
            raise RuntimeError("Repository not initialized")

        existing = await self.repository.get_by_account(account_id)
        
        if existing and (not exclude_binding_id or existing.id != exclude_binding_id):
            raise AccountAlreadyBoundError(
                account_id=account_id,
                existing_binding_id=existing.id,
            )

    async def bind_account_to_server(
        self,
        session_id: int,
        server_id: int,
        account_id: int,
        priority: int = 1,
        description: str | None = None,
        notes: str | None = None,
    ) -> Binding:
        """Bind an account to a server for a session.

        Returns the created binding.
        Raises AccountAlreadyBoundError if account is already bound.
        """
        if not self.repository:
            raise RuntimeError("Repository not initialized")

        # Validate account not already bound
        await self.validate_account_not_bound(account_id)

        # Create binding
        binding = Binding.create(
            session_id=session_id,
            server_id=server_id,
            account_id=account_id,
            priority=priority,
            description=description,
            notes=notes,
        )

        return binding

    async def bulk_bind_accounts(
        self,
        session_id: int,
        server_id: int,
        account_ids: list[int],
        priority: int = 1,
        description: str | None = None,
        notes: str | None = None,
    ) -> list[Binding]:
        """Bind multiple accounts to a server for a session.

        Returns list of created bindings.
        Raises AccountAlreadyBoundError if any account is already bound.
        """
        if not self.repository:
            raise RuntimeError("Repository not initialized")

        # Validate all accounts first
        for account_id in account_ids:
            await self.validate_account_not_bound(account_id)

        # Create bindings
        bindings = []
        for account_id in account_ids:
            binding = Binding.create(
                session_id=session_id,
                server_id=server_id,
                account_id=account_id,
                priority=priority,
                description=description,
                notes=notes,
            )
            bindings.append(binding)

        return bindings

    @staticmethod
    def get_workflow_steps() -> list[str]:
        """Return list of valid workflow steps."""
        return ["BINDED", "REQUEST_OTP", "VERIFY_OTP", "VERIFIED", "LOGGED_OUT"]

    @staticmethod
    def is_terminal_step(step: str) -> bool:
        """Check if a workflow step is terminal (no further transitions)."""
        return step == "LOGGED_OUT"

    @staticmethod
    def is_ready_for_transactions(step: str, is_active: bool) -> bool:
        """Check if binding is ready for transactions."""
        return step == "VERIFIED" and is_active
