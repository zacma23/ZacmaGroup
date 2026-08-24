"""Telebirr Mobile Money Payment Adapter.

Handles Telebirr merchant payments, USSD/SuperApp payment flows,
and configurable customer-facing merchant numbers.
"""

from typing import Any, Optional
from app.services.payment_adapters.base import BasePaymentAdapter


class TelebirrPaymentAdapter(BasePaymentAdapter):
    """Adapter for Ethio Telecom Telebirr Mobile Money."""

    def initialize_payment(
        self,
        transaction: dict[str, Any],
        return_url: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate Telebirr mobile payment instructions."""
        merchant_no = self.config.get("customer_payment_number") or self.config.get("account_number") or "+251911000001"
        account_name = self.config.get("account_name") or "Zacma Technology Group"
        tx_ref = transaction.get("public_reference")
        amount = transaction.get("amount", 0.0)
        currency = transaction.get("currency", "ETB")

        instructions = (
            f"Please send {amount:,.2f} {currency} via Telebirr:\n"
            f"• Telebirr Merchant Number: {merchant_no}\n"
            f"• Merchant / Account Name: {account_name}\n"
            f"• Payment Reason / Transaction Reference: {tx_ref}\n\n"
            f"Pay via Telebirr SuperApp or dial *127#, complete transfer with reference '{tx_ref}', and upload transaction SMS/screenshot in Client Portal (/portal)."
        )

        return {
            "success": True,
            "checkout_url": None,
            "status": "pending",
            "provider_reference": tx_ref,
            "account_name": account_name,
            "customer_payment_number": merchant_no,
            "instructions": instructions,
        }

    def verify_payment(self, transaction: dict[str, Any]) -> dict[str, Any]:
        """Verify Telebirr transaction."""
        is_successful = transaction.get("status") == "successful"
        tx_ref = transaction.get("public_reference")

        return {
            "success": is_successful,
            "status": "successful" if is_successful else "pending",
            "provider_transaction_id": transaction.get("provider_transaction_id"),
            "provider_reference": tx_ref,
            "amount": transaction.get("amount", 0.0),
            "currency": transaction.get("currency", "ETB"),
            "message": "Telebirr payment verified" if is_successful else "Awaiting Telebirr transaction confirmation",
        }

    def get_balance(self) -> dict[str, Any]:
        return {
            "supported": False,
            "balance": None,
            "currency": self.config.get("currency", "ETB"),
            "message": "Balance unavailable from provider API (Maintained via internal platform balance)",
        }

    def test_connection(self) -> dict[str, Any]:
        merchant_no = self.config.get("customer_payment_number") or self.config.get("account_number")
        if not merchant_no:
            return {
                "success": False,
                "message": "Telebirr customer payment/merchant number is not configured.",
            }

        return {
            "success": True,
            "message": f"Telebirr Mobile Money active for Merchant: {merchant_no}.",
        }
