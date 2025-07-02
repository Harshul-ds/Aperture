#!/bin/bash

# This script is now the single source of truth for resetting the environment.

CHROMA_DB_PATH="./chroma_db"
SQL_DB_PATH="./aperture_local.db"

# Check if the special '--reset' flag was passed as the first argument.
if [ "$1" == "--reset" ]; then
  echo "--- Reset flag detected. Wiping all databases BEFORE starting the application. ---"
  
  # Use the file system's "sledgehammer" to remove the databases.
  # This happens before any Python code is imported, guaranteeing a clean state.
  echo "Deleting old databases..."
  rm -rf "$CHROMA_DB_PATH"
  rm -f "$SQL_DB_PATH"
  echo "Databases wiped."
fi

# The rest of the script is for starting the application as normal.
# Clean up any leftover processes from a bad shutdown
killall x11vnc Xvfb || true
sleep 1

# Start virtual screen
echo "Starting virtual screen on :99..."
Xvfb :99 -screen 0 1280x800x24 &
sleep 2

# Start VNC server
echo "Starting VNC server on port 5900. Password is 'aperture'"
x11vnc -display :99 -forever -passwd aperture -quiet &
sleep 1

# Start the Electron application
echo "Starting Aperture application..."
DISPLAY=:99 ./node_modules/.bin/electron . --no-sandbox --disable-gpu

echo "Application closed. Shutting down."
killall x11vnc Xvfb