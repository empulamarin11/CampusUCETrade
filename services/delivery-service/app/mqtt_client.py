# app/mqtt_client.py
import json
import logging
import paho.mqtt.client as mqtt

from app.config import settings
from app.db import SessionLocal
from app.handlers import handle_create, handle_confirm

log = logging.getLogger("delivery.mqtt")


def build_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(client_id=settings.mqtt_client_id, protocol=mqtt.MQTTv311)

    if settings.mqtt_username:
        client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

    def on_connect(c, userdata, flags, rc):
        if rc == 0:
            log.info("MQTT connected")
            c.subscribe(settings.topic_create, qos=1)
            c.subscribe(settings.topic_confirm, qos=1)
        else:
            log.error("MQTT connect failed rc=%s", rc)

    def on_message(c, userdata, msg):
        db = SessionLocal()
        try:
            payload = json.loads(msg.payload.decode("utf-8"))

            if msg.topic == settings.topic_create:
                result = handle_create(db, payload)
                log.info("CREATE ok %s", result)

            elif msg.topic == settings.topic_confirm:
                result = handle_confirm(db, payload)
                log.info("CONFIRM ok %s", result)

                # Si ya está entregado, publicamos evento
                if result.get("status") == "DELIVERED":
                    c.publish(settings.topic_delivered, json.dumps(result), qos=1, retain=False)
                    log.info("PUBLISHED delivered event %s", result)

        except Exception as e:
            log.exception("MQTT message error: %s", e)
        finally:
            db.close()

    client.on_connect = on_connect
    client.on_message = on_message
    return client
