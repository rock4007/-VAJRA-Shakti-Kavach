#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[bootstrap] syncing Go modules"
(
  cd "$ROOT_DIR/pillar1-morphic" && go mod tidy
  cd "$ROOT_DIR/pillar2-consensus" && go mod tidy
  cd "$ROOT_DIR/stability-engine" && go mod tidy
)

echo "[bootstrap] installing frontend dependencies"
(
  cd "$ROOT_DIR/frontend"
  npm install
)

echo "[bootstrap] installing entropy dependencies"
(
  cd "$ROOT_DIR/pillar3-entropy"
  python3 -m pip install -r requirements.txt
)

echo "[bootstrap] done"
