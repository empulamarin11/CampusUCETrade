import json
import os
import logging
from typing import Any, Dict, Optional

import pika

logger = logging.getLogger("mq")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = os.getenv("RABBITMQ_EXCHANGE", "campus.events")
EXCHANGE_TYPE = os.getenv("RABBITMQ_EXCHANGE_TYPE", "topic")


def _get_connection() -> pika.BlockingConnection:
    # Connect using AMQP URL (recommended for Docker Compose)
    params = pika.URLParameters(RABBITMQ_URL)
    params.heartbeat = 30
    params.blocked_connection_timeout = 30
    return pika.BlockingConnection(params)


def publish_event(routing_key: str, payload: Dict[str, Any]) -> None:
    """
    Publish an event to RabbitMQ.
    Non-fatal: if Rabbit is down, we log and continue (so API doesn't break).
    """
    try:
        conn = _get_connection()
        ch = conn.channel()

        # Ensure exchange exists (durable topic exchange)
        ch.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True,
        )

        body = json.dumps(payload).encode("utf-8")

        ch.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,  # persistent
            ),
        )

        conn.close()
    except Exception as e:
        logger.warning("Failed to publish event (%s): %s", routing_key, str(e))
