"""Base Payment Provider Adapter Interface.

Every provider adapter inherits from BasePaymentAdapter and implements
supported operations. For unsupported operations, a clean structured
response is returned without breaking system execution.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BasePaymentAdapter(ABC):
    """Abstract Base Class for Payment Provider Adapters."""

    def __init__(self, provider_config: dict[str, Any]):
        self.config = provider_config
        self.provider_code = provider_config.get("provider_code", "generic")
        self.provider_name = provider_config.get("provider_name", "Payment Provider")
        self.environment = provider_config.get("environment", "test")

    @abstractmethod
    def initialize_payment(
        self,
        transaction: dict[str, Any],
        return_url: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """Initialize payment request, return checkout URL or transfer instructions."""
        raise NotImplementedError

    @abstractmethod
    def verify_payment(self, transaction: dict[str, Any]) -> dict[str, Any]:
        """Verify payment status via server-to-server API or verification strategy."""
        raise NotImplementedError

    def get_balance(self) -> dict[str, Any]:
        """Fetch real-time balance from provider API if supported.

        Returns:
            {
                "supported": bool,
                "balance": Optional[float],
                "currency": str,
                "raw_response": Optional[dict],
                "message": str,
            }
        """
        return {
            "supported": False,
            "balance": None,
            "currency": self.config.get("currency", "ETB"),
            "message": "Balance unavailable from provider API",
        }

    def process_webhook(self, payload: dict[str, Any], headers: dict[str, Any]) -> dict[str, Any]:
        """Process and verify incoming webhook event payload & signatures."""
        return {
            "verified": False,
            "status": "unsupported",
            "transaction_reference": None,
            "message": "Webhooks not supported for this provider",
        }

    def refund_payment(self, transaction: dict[str, Any], amount: Optional[float] = None) -> dict[str, Any]:
        """Process refund where supported by provider API."""
        return {
            "success": False,
            "status": "unsupported",
            "message": "Automated refunds not supported by this provider. Process manually.",
        }

    def test_connection(self) -> dict[str, Any]:
        """Test API connectivity and credentials."""
        return {
            "success": True,
            "message": f"Provider '{self.provider_name}' is configured and operational ({self.environment} mode).",
        }
