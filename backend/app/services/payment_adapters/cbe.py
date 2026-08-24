"""Commercial Bank of Ethiopia (CBE) Payment Adapter.

Provides configurable bank transfer handling, dynamic account information
managed from the Admin Dashboard, and structured verification workflow.
"""

from typing import Any, Optional
from app.services.payment_adapters.base import BasePaymentAdapter


class CbePaymentAdapter(BasePaymentAdapter):
    """Adapter for Commercial Bank of Ethiopia (CBE)."""

    def initialize_payment(
        self,
        transaction: dict[str, Any],
        return_url: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate CBE bank transfer payment instructions."""
        account_name = self.config.get("account_name") or "Zacma Technology Group"
        account_number = self.config.get("account_number") or "Configured in Admin Dashboard"
        cust_pay_no = self.config.get("customer_payment_number") or "CBE-ZACMA-PAY"
        tx_ref = transaction.get("public_reference")
        amount = transaction.get("amount", 0.0)
        currency = transaction.get("currency", "ETB")

        instructions = (
            f"Please transfer {amount:,.2f} {currency} to Commercial Bank of Ethiopia (CBE).\n"
            f"• Account Name: {account_name}\n"
            f"• Account Number: {account_number}\n"
            f"• Customer Payment Number: {cust_pay_no}\n"
            f"• Payment Reason / Reference: {tx_ref}\n\n"
            f"After completing the transfer, upload your bank transaction receipt in the Client Portal (/portal) for instant verification."
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
        """Verify CBE payment proof."""
        # If invoice or transaction already has a verified payment attempt
        tx_ref = transaction.get("public_reference")
        is_already_success = transaction.get("status") == "successful"

        return {
            "success": is_already_success,
            "status": "successful" if is_already_success else "pending",
            "provider_transaction_id": transaction.get("provider_transaction_id"),
            "provider_reference": tx_ref,
            "amount": transaction.get("amount", 0.0),
            "currency": transaction.get("currency", "ETB"),
            "message": "CBE Transfer awaiting receipt confirmation" if not is_already_success else "CBE Transfer verified",
        }

    def get_balance(self) -> dict[str, Any]:
        """CBE bank transfers do not have a public balance API."""
        return {
            "supported": False,
            "balance": None,
            "currency": self.config.get("currency", "ETB"),
            "message": "Balance unavailable from provider API (Maintained via internal platform balance)",
        }

    def test_connection(self) -> dict[str, Any]:
        """Validate CBE configuration in Admin Dashboard."""
        account_no = self.config.get("account_number")
        account_name = self.config.get("account_name")

        if not account_no or not account_name:
            return {
                "success": False,
                "message": "CBE configuration incomplete. Please configure Account Name and Account Number in Admin Payment Settings.",
            }

        return {
            "success": True,
            "message": f"CBE Bank Transfer provider active for Account: {account_name} ({account_no}).",
        }
