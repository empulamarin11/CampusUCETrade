#!/usr/bin/env bash
set -e

# Ir a la raíz del repo aunque ejecutes desde /bdd
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Cargar variables del estudiante
set -a
source students/campusucetrade/config.env
set +a

echo "BASE_URL=$BASE_URL"
echo "Smoke: $BASE_URL/auth/health"
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$BASE_URL/auth/health" || true

echo "Running BDD..."
behave features -f pretty
