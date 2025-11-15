#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting deployment for Call Transcriber Service"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "📁 Repo root: ${REPO_ROOT}"

# Install Docker if missing
if ! command -v docker &> /dev/null; then
  echo "🐳 Docker not found. Installing..."
  sudo apt-get update -y
  sudo apt-get install -y docker.io
  sudo systemctl enable docker
  sudo systemctl start docker
else
  echo "🐳 Docker already installed."
fi

# Install docker-compose if missing
if ! command -v docker-compose &> /dev/null; then
  echo "📦 docker-compose not found. Installing..."
  sudo curl -SL "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64" \
    -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
else
  echo "📦 docker-compose already installed."
fi

echo "🔄 Fetching latest code from main..."
git fetch origin
git checkout main
git reset --hard origin/main
git clean -fd

echo "🧹 Cleaning up old Docker resources (optional)..."
docker system prune -af || true
docker volume prune -f || true

echo "📦 Building and starting containers..."
docker-compose up --build -d

echo "✅ Deployment complete. Service should be available on port 8000."