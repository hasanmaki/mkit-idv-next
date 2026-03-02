"""Binding command handlers - application service layer."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.bindings.commands import (
    BindAccountCommand,
    BulkBindAccountsCommand,
    ReleaseBindingCommand,
    RequestOTPCommand,
    SetBalanceStartCommand,
    VerifyOTPCommand,
)
from app.core.exceptions import AppValidationError
from app.domain.bindings.entities import Binding
from app.domain.bindings.exceptions import BindingNotFoundError
from app.domain.bindings.services import BindingDomainService
from app.models.bindings import Bindings
from app.repos.binding_repo import BindingRepository


class BindingCommandHandler:
    """Application service for handling binding commands."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BindingRepository(Bindings)
        self.domain_service = BindingDomainService(self.repo)

    async def handle_bind(self, command: BindAccountCommand) -> Binding:
        """Handle bind account command."""
        # Create binding entity
        binding_entity = await self.domain_service.bind_account_to_server(
            session_id=command.session_id,
            server_id=command.server_id,
            account_id=command.account_id,
            priority=command.priority,
            description=command.description,
            notes=command.notes,
        )

        # Persist
        binding_data = binding_entity.model_dump(exclude={"_domain_events"})
        persisted_binding = await self.repo.create(self.session, **binding_data)

        return persisted_binding

    async def handle_bulk_bind(
        self,
        command: BulkBindAccountsCommand,
    ) -> list[Binding]:
        """Handle bulk bind accounts command."""
        # Create binding entities
        binding_entities = await self.domain_service.bulk_bind_accounts(
            session_id=command.session_id,
            server_id=command.server_id,
            account_ids=command.account_ids,
            priority=command.priority,
            description=command.description,
            notes=command.notes,
        )

        # Persist all
        persisted_bindings = []
        for binding_entity in binding_entities:
            binding_data = binding_entity.model_dump(exclude={"_domain_events"})
            persisted = await self.repo.create(self.session, **binding_data)
            persisted_bindings.append(persisted)

        return persisted_bindings

    async def handle_request_otp(self, command: RequestOTPCommand) -> Binding:
        """Handle request OTP command."""
        # Get existing binding
        existing = await self.repo.get(self.session, command.binding_id)
        if not existing:
            raise BindingNotFoundError(binding_id=command.binding_id)

        # Load as domain entity
        binding_entity = Binding.model_validate(existing)

        # Request OTP
        binding_entity.request_otp()

        # Persist
        persisted = await self.repo.update(
            self.session,
            existing,
            step=binding_entity.step,
            device_id=binding_entity.device_id,
            last_used_at=binding_entity.last_used_at,
        )

        return persisted

    async def handle_verify_otp(self, command: VerifyOTPCommand) -> Binding:
        """Handle verify OTP command."""
        # Get existing binding
        existing = await self.repo.get(self.session, command.binding_id)
        if not existing:
            raise BindingNotFoundError(binding_id=command.binding_id)

        # Load as domain entity
        binding_entity = Binding.model_validate(existing)

        # Verify OTP (transition to VERIFY_OTP first)
        binding_entity.verify_otp(device_id=binding_entity.device_id)

        # Persist
        persisted = await self.repo.update(
            self.session,
            existing,
            step=binding_entity.step,
            last_used_at=binding_entity.last_used_at,
        )

        return persisted

    async def handle_mark_verified(self, binding_id: int) -> Binding:
        """Mark binding as verified (after OTP success)."""
        # Get existing binding
        existing = await self.repo.get(self.session, binding_id)
        if not existing:
            raise BindingNotFoundError(binding_id=binding_id)

        # Load as domain entity
        binding_entity = Binding.model_validate(existing)

        # Mark as verified
        binding_entity.mark_verified()

        # Persist
        persisted = await self.repo.update(
            self.session,
            existing,
            step=binding_entity.step,
            last_used_at=binding_entity.last_used_at,
        )

        return persisted

    async def handle_release(self, command: ReleaseBindingCommand) -> None:
        """Handle release binding command."""
        # Get existing binding
        existing = await self.repo.get(self.session, command.binding_id)
        if not existing:
            raise BindingNotFoundError(binding_id=command.binding_id)

        # Load as domain entity and release
        binding_entity = Binding.model_validate(existing)
        binding_entity.release()

        # Persist
        await self.repo.update(
            self.session,
            existing,
            step=binding_entity.step,
            is_active=False,
            last_used_at=binding_entity.last_used_at,
        )

    async def handle_set_balance(
        self,
        command: SetBalanceStartCommand,
    ) -> Binding:
        """Handle set balance start command."""
        # Get existing binding
        existing = await self.repo.get(self.session, command.binding_id)
        if not existing:
            raise BindingNotFoundError(binding_id=command.binding_id)

        # Update balance
        updated = await self.repo.update(
            self.session,
            existing,
            balance_start=command.balance_start,
            balance_source=command.source,
        )

        return updated
