#!/bin/bash

cd "$(dirname "$0")"
python3 main.py
if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to launch PyCade. Make sure Python and pygame are installed."
    echo "Run: pip install -r requirements.txt"
fi
