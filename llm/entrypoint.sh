#!/bin/bash

/bin/ollama serve &
pid=$!

sleep 5

echo "Pulling model..."
ollama pull tinyllama
echo "Pulled model!"

wait $pid