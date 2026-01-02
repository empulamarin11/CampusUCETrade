#!/bin/bash
set -euxo pipefail

# Logs to file + system console
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

APP_DIR="/opt/campusucetrade"
REPO_URL="https://github.com/empulamarin11/CampusUCETrade.git"
BRANCH="dev"
REPO_NAME="CampusUCETrade"

echo "==> Updating system and installing dependencies..."
dnf -y update

# IMPORTANT:
# - No instalamos docker-compose-plugin (no existe en algunos AL2023)
# - No tocamos curl (evitamos conflicto curl vs curl-minimal)
dnf -y install docker git wget

echo "==> Enabling and starting Docker..."
systemctl enable docker
systemctl start docker

echo "==> Installing Docker Compose v2 plugin (manual)..."
mkdir -p /usr/local/lib/docker/cli-plugins

if ! docker compose version >/dev/null 2>&1; then
  ARCH="$(uname -m)"
  case "$ARCH" in
    x86_64) COMPOSE_ARCH="x86_64" ;;
    aarch64) COMPOSE_ARCH="aarch64" ;;
    *) echo "Unsupported arch: $ARCH"; exit 1 ;;
  esac

  COMPOSE_VERSION="v2.27.0"

  wget -O /usr/local/lib/docker/cli-plugins/docker-compose \
    "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-${COMPOSE_ARCH}"

  chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

docker compose version || true

echo "==> Preparing app directory..."
mkdir -p "${APP_DIR}"
cd "${APP_DIR}"

echo "==> Cloning or updating repository..."
if [ ! -d "${APP_DIR}/${REPO_NAME}/.git" ]; then
  rm -rf "${APP_DIR}/${REPO_NAME}" || true
  git clone --depth 1 --branch "${BRANCH}" "${REPO_URL}" "${REPO_NAME}"
else
  cd "${APP_DIR}/${REPO_NAME}"
  git fetch origin "${BRANCH}"
  git checkout "${BRANCH}"
  git reset --hard "origin/${BRANCH}"
fi

cd "${APP_DIR}/${REPO_NAME}"

echo "==> Starting docker compose stack..."
docker compose down || true
docker compose up -d --build

echo "==> Local health check (wget)..."
wget -qO- http://localhost/ || true

echo "==> Done. Containers:"
docker ps || true
