"""Generic Bank / Payment Provider Adapter.

Allows administrators to add and configure any Ethiopian bank or payment
channel (Awash Bank, Bank of Abyssinia, Dashen Bank, Hibret Bank, etc.)
dynamically without code modifications.
"""

from typing import Any, Optional
from app.services.payment_adapters.base import BasePaymentAdapter


class GenericBankPaymentAdapter(BasePaymentAdapter):
    """Dynamic adapter for any configured bank or payment provider."""

    def initialize_payment(
        self,
        transaction: dict[str, Any],
        return_url: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate bank transfer instructions for this provider."""
        bank_name = self.config.get("provider_name") or "Bank Transfer"
        account_name = self.config.get("account_name") or "Zacma Technology Group"
        account_number = self.config.get("account_number") or self.config.get("customer_payment_number") or "Configured in Settings"
        cust_pay_no = self.config.get("customer_payment_number")
        tx_ref = transaction.get("public_reference")
        amount = transaction.get("amount", 0.0)
        currency = transaction.get("currency", "ETB")

        custom_instructions = self.config.get("instructions")
        if custom_instructions:
            instructions = f"{custom_instructions}\n• Reference: {tx_ref}\n• Amount: {amount:,.2f} {currency}"
        else:
            instructions = (
                f"Please transfer {amount:,.2f} {currency} to {bank_name}.\n"
                f"• Account Name: {account_name}\n"
                f"• Account / Reference Number: {account_number}\n"
                f"• Transaction Reference Code: {tx_ref}\n\n"
                f"After transfer, upload your payment receipt in the Client Portal (/portal)."
            )

        return {
            "success": True,
            "checkout_url": None,
            "status": "pending",
            "provider_reference": tx_ref,
            "account_name": account_name,
            "account_number": account_number,
            "customer_payment_number": cust_pay_no,
            "instructions": instructions,
        }

    def verify_payment(self, transaction: dict[str, Any]) -> dict[str, Any]:
        is_successful = transaction.get("status") == "successful"
        tx_ref = transaction.get("public_reference")

        return {
            "success": is_successful,
            "status": "successful" if is_successful else "pending",
            "provider_transaction_id": transaction.get("provider_transaction_id"),
            "provider_reference": tx_ref,
            "amount": transaction.get("amount", 0.0),
            "currency": transaction.get("currency", "ETB"),
            "message": f"{self.provider_name} payment verified" if is_successful else f"Awaiting {self.provider_name} receipt confirmation",
        }

    def get_balance(self) -> dict[str, Any]:
        return {
            "supported": False,
            "balance": None,
            "currency": self.config.get("currency", "ETB"),
            "message": "Balance unavailable from provider API (Maintained via internal platform balance)",
        }

    def test_connection(self) -> dict[str, Any]:
        account_no = self.config.get("account_number") or self.config.get("customer_payment_number")
        if not account_no:
            return {
                "success": False,
                "message": f"{self.provider_name} configuration missing Account/Payment Number.",
            }
        return {
            "success": True,
            "message": f"{self.provider_name} active and configured.",
        }
