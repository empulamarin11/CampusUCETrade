# MQTT Broker Config — `docker/mqtt`

This folder contains the configuration for the **MQTT broker** used by CampusUCETrade (Mosquitto).  
It is part of the **middleware block** and is typically started via Docker Compose inside:

- `deploy/qa/middleware/`
- `deploy/prod/middleware/`

---

## 1) Contents

docker/mqtt/
mosquitto.conf


### `mosquitto.conf`
Defines Mosquitto settings such as:
- listener port (commonly `1883`)
- persistence options
- authentication/authorization rules (if enabled)
- logging behavior

---

## 2) How It’s Used

The middleware Docker Compose mounts this config file into the container, for example:

- Mount path (typical):
  - `/mosquitto/config/mosquitto.conf`

The realtime services (or any MQTT-based service) connect to:
- `MQTT_HOST=<middleware_private_ip>`
- `MQTT_PORT=1883`

---

## 3) Notes / Best Practices
- If authentication is enabled, do **not** commit broker passwords into Git.
- For PROD, prefer restricting broker access to the private network only (security groups).
- Keep config changes backwards compatible (clients can be sensitive to broker 