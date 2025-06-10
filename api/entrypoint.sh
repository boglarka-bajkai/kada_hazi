#!/bin/bash

set -e

MODEL="${MODEL:-tinyllama}"

echo "Waiting for Ollama..."

until curl -s "ollama:11434/api/tags" | grep "$MODEL"; do
    echo "Not ready yet..."
    sleep 5
done

echo "Ollama ready!"

exec uvicorn main:app --host 0.0.0.0 --port 8000
