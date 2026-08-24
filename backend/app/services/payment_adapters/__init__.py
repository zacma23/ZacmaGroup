"""Payment Provider Adapters Package for ZACMA Multi-Provider Platform."""

from app.services.payment_adapters.base import BasePaymentAdapter
from app.services.payment_adapters.chapa import ChapaPaymentAdapter
from app.services.payment_adapters.cbe import CbePaymentAdapter
from app.services.payment_adapters.telebirr import TelebirrPaymentAdapter
from app.services.payment_adapters.generic_bank import GenericBankPaymentAdapter
from app.services.payment_adapters.santimpay import SantimPayPaymentAdapter

__all__ = [
    "BasePaymentAdapter",
    "ChapaPaymentAdapter",
    "CbePaymentAdapter",
    "TelebirrPaymentAdapter",
    "GenericBankPaymentAdapter",
    "SantimPayPaymentAdapter",
]
