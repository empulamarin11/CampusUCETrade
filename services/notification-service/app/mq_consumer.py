import json
import os
import threading
import time
from datetime import datetime, timezone
from uuid import uuid4

import pika
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Notification

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "campus.events")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "notification-service")
RABBITMQ_BINDINGS = os.getenv("RABBITMQ_BINDINGS", "reservation.*")  # comma-separated
RABBITMQ_PREFETCH = int(os.getenv("RABBITMQ_PREFETCH", "20"))

_stop_event = threading.Event()


def _safe_json(body: bytes) -> dict:
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return {}


def _create_notification_from_event(db: Session, event: dict) -> None:
    event_type = str(event.get("type", "")).strip()
    requester_email = str(event.get("requester_email", "")).strip().lower()

    if not requester_email:
        return

    # Simple MVP mapping
    title = "Event"
    message = f"New event: {event_type}"

    if event_type == "reservation.created":
        title = "Reservation created"
        message = f"Your reservation was created for item {event.get('item_id', '')}"
    elif event_type.startswith("reservation."):
        # e.g. reservation.cancelled, reservation.confirmed
        status = event_type.split(".", 1)[1]
        title = "Reservation updated"
        message = f"Your reservation status is now: {status}"

    now = datetime.now(timezone.utc)

    row = Notification(
        id=str(uuid4()),
        user_email=requester_email,
        title=title,
        message=message,
        type="info",
        created_at=now,
        read=False,
    )

    db.add(row)
    db.commit()


def _on_message(ch, method, properties, body):
    event = _safe_json(body)

    db = SessionLocal()
    try:
        _create_notification_from_event(db, event)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        # If DB fails, requeue could cause infinite loops; keep it simple for MVP:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    finally:
        db.close()


def consume_forever() -> None:
    while not _stop_event.is_set():
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="topic", durable=True)
            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

            bindings = [b.strip() for b in RABBITMQ_BINDINGS.split(",") if b.strip()]
            for binding in bindings:
                channel.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=RABBITMQ_QUEUE, routing_key=binding)

            channel.basic_qos(prefetch_count=RABBITMQ_PREFETCH)
            channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=_on_message, auto_ack=False)

            channel.start_consuming()

        except Exception:
            # Rabbit might not be ready yet
            time.sleep(2)

        finally:
            try:
                connection.close()
            except Exception:
                pass


def start_consumer_thread() -> None:
    t = threading.Thread(target=consume_forever, name="rabbit-consumer", daemon=True)
    t.start()


def stop_consumer() -> None:
    _stop_event.set()
