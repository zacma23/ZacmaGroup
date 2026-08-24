"""Shared Notification Engine Service.

Handles automated transactional email delivery for invoices, payment confirmations,
approvals, document requests, and ticket updates with templated hydration.
"""

import logging
from typing import Any, Optional

from app.core.config import settings
from app.core.demo_data import notification_templates_store

logger = logging.getLogger("zacma.notifications")


class NotificationService:
    @staticmethod
    def get_template(key: str, tenant_id: str = "zacma-demo") -> Optional[dict[str, Any]]:
        """Fetch template by key from demo store or DB."""
        templates = notification_templates_store.list_all(tenant_id)
        for t in templates:
            if t.get("key") == key:
                return t
        return None

    @staticmethod
    def send_email(
        to_email: str,
        template_key: str,
        model: dict[str, Any],
        tenant_id: str = "zacma-demo",
    ) -> dict[str, Any]:
        """Hydrate template and dispatch email."""
        template = NotificationService.get_template(template_key, tenant_id)

        if template:
            try:
                subject = template["subject"].format(**model)
                body = template["body_template"].format(**model)
            except KeyError as e:
                subject = f"Zacma Notification: {template_key}"
                body = f"Notification ({template_key}): Missing template variable {e}"
        else:
            subject = f"Zacma Notification ({template_key})"
            body = "\n".join([f"{k}: {v}" for k, v in model.items()])

        # In local/demo mode, log email dispatch cleanly
        logger.info(
            "[EMAIL DISPATCH] To: %s | Subject: %s | From: %s",
            to_email,
            subject,
            settings.mail_from,
        )
        logger.debug("[EMAIL BODY]\n%s", body)

        return {
            "status": "sent",
            "to": to_email,
            "subject": subject,
            "preview_body": body[:200] + "..." if len(body) > 200 else body,
            "template_key": template_key,
        }
