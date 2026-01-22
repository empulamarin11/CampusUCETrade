import json
import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger("webhook")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "").strip()
N8N_WEBHOOK_TIMEOUT = float(os.getenv("N8N_WEBHOOK_TIMEOUT", "5.0"))


def send_to_n8n(event: Dict[str, Any]) -> None:
    """
    Fire-and-forget webhook call to n8n.
    Non-fatal: if n8n is not configured/down, we log and continue.
    """
    if not N8N_WEBHOOK_URL:
        return

    try:
        with httpx.Client(timeout=N8N_WEBHOOK_TIMEOUT) as client:
            client.post(
                N8N_WEBHOOK_URL,
                content=json.dumps(event),
                headers={"Content-Type": "application/json"},
            )
    except Exception as e:
        logger.warning("Failed to call n8n webhook: %s", str(e))
