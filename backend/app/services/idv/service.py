"""Service layer for IDV provider endpoints."""

from typing import Any

from app.core.clients import BaseHTTPClient
from app.core.exceptions import AppValidationError
from app.core.log_config import get_logger
from app.models.servers import Servers

logger = get_logger("service.idv")


class IdvService:
    """Service wrapper for IDV endpoints defined in project.md."""

    def __init__(
        self,
        base_url: str,
        timeout: float | None = None,
        retries: int | None = None,
        wait_between_retries: float | None = None,
        max_requests_queued: int | None = None,
    ) -> None:
        backoff_factor = wait_between_retries
        self.client = BaseHTTPClient(
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            max_connections=max_requests_queued,
            service_name="idv",
        )

    @classmethod
    def from_server(cls, server: Servers) -> "IdvService":
        """Create service from Servers model settings."""
        return cls(
            base_url=server.base_url,
            timeout=float(server.timeout),
            retries=server.retries,
            wait_between_retries=float(server.wait_between_retries),
            max_requests_queued=server.max_requests_queued,
        )

    async def request_otp(self, username: str, pin: str) -> dict[str, Any]:
        """Request OTP."""
        self._validate_required("username", username)
        self._validate_required("pin", pin)
        logger.info("Request OTP", extra={"username": username})
        return await self.client.request_json(
            "GET",
            "/otp",
            params={"username": username, "pin": pin},
        )

    async def verify_otp(self, username: str, otp: str) -> dict[str, Any]:
        """Verify OTP."""
        self._validate_required("username", username)
        self._validate_required("otp", otp)
        logger.info("Verify OTP", extra={"username": username})
        return await self.client.request_json(
            "GET",
            "/verifyOtp",
            params={"username": username, "otp": otp},
        )

    async def logout(self, username: str) -> dict[str, Any]:
        """Logout."""
        self._validate_required("username", username)
        logger.info("Logout", extra={"username": username})
        return await self.client.request_json(
            "GET",
            "/logout",
            params={"username": username},
        )

    async def get_balance_pulsa(self, username: str) -> dict[str, Any]:
        """Get balance pulsa."""
        self._validate_required("username", username)
        logger.info("Get balance pulsa", extra={"username": username})
        return await self.client.request_json(
            "GET",
            "/balance_pulsa",
            params={"username": username},
        )

    async def get_token_location3(self, username: str) -> dict[str, Any]:
        """Get token location3."""
        self._validate_required("username", username)
        logger.info("Get token location3", extra={"username": username})
        token = await self.client.request_text(
            "GET",
            "/token_location3",
            params={"username": username},
        )
        return {"token": token}

    async def list_produk(self, username: str) -> dict[str, Any]:
        """List produk."""
        self._validate_required("username", username)
        logger.info("List produk", extra={"username": username})
        return await self.client.request_json(
            "GET",
            "/list_idv",
            params={"username": username},
        )

    async def trx_voucher_idv(
        self,
        username: str,
        product_id: str,
        email: str,
        limit_harga: int,
    ) -> dict[str, Any]:
        """Transaksi voucher IDV."""
        self._validate_required("username", username)
        self._validate_required("product_id", product_id)
        self._validate_required("email", email)
        if limit_harga <= 0:
            raise AppValidationError(
                message="limit_harga harus lebih dari 0.",
                error_code="idv_invalid_limit_harga",
                context={"limit_harga": limit_harga},
            )
        logger.info(
            "Trx voucher IDV",
            extra={"username": username, "product_id": product_id},
        )
        return await self.client.request_json(
            "GET",
            "/trx_idv",
            params={
                "username": username,
                "product_id": product_id,
                "email": email,
                "limit_harga": limit_harga,
            },
        )

    async def otp_trx(self, username: str, otp: str) -> dict[str, Any]:
        """OTP transaksi IDV."""
        self._validate_required("username", username)
        self._validate_required("otp", otp)
        logger.info("OTP transaksi", extra={"username": username})
        return await self.client.request_json(
            "GET",
            "/otp_idv",
            params={"username": username, "otp": otp},
        )

    async def status_trx(self, username: str, trx_id: str) -> dict[str, Any]:
        """Status transaksi IDV."""
        self._validate_required("username", username)
        self._validate_required("trx_id", trx_id)
        logger.info("Status transaksi", extra={"username": username, "trx_id": trx_id})
        return await self.client.request_json(
            "GET",
            "/status_idv",
            params={"username": username, "trx_id": trx_id},
        )

    async def flow_login(self, username: str, pin: str, otp: str) -> dict[str, Any]:
        """Flow login: request otp -> verify otp -> balance -> token -> list."""
        logger.info("Start flow login", extra={"username": username})
        request_otp = await self.request_otp(username, pin)
        verify_otp = await self.verify_otp(username, otp)
        balance = await self.get_balance_pulsa(username)
        token = await self.get_token_location3(username)
        list_produk = await self.list_produk(username)
        return {
            "request_otp": request_otp,
            "verify_otp": verify_otp,
            "balance": balance,
            "token": token,
            "list_produk": list_produk,
        }

    async def flow_first_transaction(
        self,
        username: str,
        product_id: str,
        email: str,
        limit_harga: int,
        otp: str,
    ) -> dict[str, Any]:
        """Flow transaksi pertama: trx -> otp -> status."""
        logger.info("Start flow transaksi pertama", extra={"username": username})
        trx = await self.trx_voucher_idv(username, product_id, email, limit_harga)
        otp_res = await self.otp_trx(username, otp)
        trx_id = self._extract_trx_id(trx)
        status = await self.status_trx(username, trx_id)
        return {"trx": trx, "otp": otp_res, "status": status}

    async def flow_next_transaction(
        self,
        username: str,
        product_id: str,
        email: str,
        limit_harga: int,
    ) -> dict[str, Any]:
        """Flow transaksi berikutnya: trx -> status."""
        logger.info("Start flow transaksi berikutnya", extra={"username": username})
        trx = await self.trx_voucher_idv(username, product_id, email, limit_harga)
        trx_id = self._extract_trx_id(trx)
        status = await self.status_trx(username, trx_id)
        return {"trx": trx, "status": status}

    @staticmethod
    def _validate_required(field_name: str, value: str) -> None:
        """Raise AppValidationError when a required field is missing or empty."""
        if not value:
            raise AppValidationError(
                message=f"{field_name} wajib diisi.",
                error_code="idv_missing_field",
                context={"field": field_name},
            )

    @staticmethod
    def _extract_trx_id(payload: dict[str, Any]) -> str:
        """Extract `trx_id` from an IDV transaction response or raise AppValidationError."""
        trx_id = payload.get("trx_id")
        if not trx_id:
            raise AppValidationError(
                message="trx_id tidak ditemukan di respons transaksi.",
                error_code="idv_missing_trx_id",
                context={"payload_keys": list(payload.keys())},
            )
        return str(trx_id)
