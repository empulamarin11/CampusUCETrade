# app/kafka_consumer.py
import json
import logging
import threading
import time

from kafka import KafkaConsumer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models import AuditEvent

logger = logging.getLogger("traceability.kafka")


def _save_event(db: Session, event_type: str, source: str, payload: dict):
    row = AuditEvent(
        event_type=event_type or "unknown",
        source=source or "unknown",
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    db.add(row)
    db.commit()


def _consume_loop():
    # Non-fatal: retry forever with backoff
    while True:
        try:
            consumer = KafkaConsumer(
                settings.kafka_topic,
                bootstrap_servers=settings.kafka_bootstrap,
                group_id=settings.kafka_group_id,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            )
            logger.info("Kafka consumer connected: %s topic=%s", settings.kafka_bootstrap, settings.kafka_topic)

            for msg in consumer:
                payload = msg.value if isinstance(msg.value, dict) else {"raw": msg.value}
                event_type = payload.get("event_type") or payload.get("type") or "unknown"
                source = payload.get("source") or "unknown"

                db = SessionLocal()
                try:
                    _save_event(db, event_type=event_type, source=source, payload=payload)
                except Exception as e:
                    logger.exception("Failed to persist audit event: %s", e)
                finally:
                    db.close()

        except Exception as e:
            logger.warning("Kafka not available yet (non-fatal). Retrying... err=%s", e)
            time.sleep(5)


def start_consumer_thread():
    t = threading.Thread(target=_consume_loop, daemon=True)
    t.start()
    return t
