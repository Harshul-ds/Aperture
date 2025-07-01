#!/bin/bash

# Set a display number
export DISPLAY=:99

# Start the virtual framebuffer (Xvfb) in the background
echo "Starting virtual screen..."
Xvfb :99 -screen 0 1280x1024x24 & 
XVFB_PID=$!

# Give Xvfb a moment to start
sleep 2

# Start the VNC server to stream the virtual display.
# It will be accessible on port 5900.
# The -forever flag keeps it running after the first connection.
# The -nopw flag means no password is required (safe for a trusted Codespace env).
echo "Starting VNC server on port 5900..."
x11vnc -display :99 -forever -nopw -quiet & 
X11VNC_PID=$!

# Run the Electron application.
# We use the full path to the executable and add flags for compatibility.
echo "Starting Aperture application..."

# Base command arguments for Electron
ELECTRON_ARGS=("."
"--no-sandbox")

# In GitHub Codespaces, a GPU is not available.
# We check for the CODESPACES environment variable and disable the GPU if it's present.
if [ "$CODESPACES" = "true" ]; then
  echo "Codespace environment detected. Disabling GPU acceleration."
  ELECTRON_ARGS+=("--disable-gpu")
fi

# Execute Electron with the constructed arguments
./node_modules/.bin/electron "${ELECTRON_ARGS[@]}"

# When the Electron app is closed, this script will continue.
# We'll now clean up the background processes.
echo "Application closed. Shutting down virtual screen and VNC server."
kill $XVFB_PID
kill $X11VNC_PID
