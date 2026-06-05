#!/bin/bash
set -e

PORT=5000
VENV_DIR="venv"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $SERVER_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Install Python 3.8+ and try again."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r requirements.txt

echo "Starting server on http://localhost:$PORT"
"$VENV_DIR/bin/uvicorn" app:app --host 0.0.0.0 --port "$PORT" &
SERVER_PID=$!

sleep 1
open "http://localhost:$PORT"

echo "Press Ctrl+C to stop the server."
wait $SERVER_PID
