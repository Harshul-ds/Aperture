#!/bin/bash

# ==============================================================================
# Aperture Project Scaffolding Script
# ==============================================================================
# This script creates the complete directory and file structure for the project.
# It is safe to run multiple times.

echo "🚀 Scaffolding Aperture project structure..."

# --- Create Core Directories ---
mkdir -p .github/workflows
mkdir -p backend/api backend/core backend/models
mkdir -p frontend/assets frontend/js
mkdir -p scripts

# --- Create Backend Files ---
touch backend/main.py
touch backend/api/__init__.py
touch backend/core/__init__.py
touch backend/models/__init__.py

# --- Create Frontend Files ---
touch frontend/index.html
touch frontend/js/renderer.js
touch frontend/preload.js
touch frontend/assets/style.css

# --- Create Root Files ---
touch main.js
touch .env.example
touch .gitignore

# --- Populate Files with Boilerplate Code ---

echo "✍️ Writing boilerplate code..."

# .gitignore
cat <<EOF > .gitignore
# Python
__pycache__/
*.pyc
.venv/
dist/
build/
*.egg-info/

# Node
node_modules/
npm-debug.log
.npm/

# macOS
.DS_Store

# Environment
.env
*.env.local

# IDE
.vscode/
.idea/
EOF

# .env.example
cat <<EOF > .env.example
# Google Cloud Credentials - DO NOT COMMIT THE REAL VALUES
GOOGLE_CLIENT_ID="your_client_id_here"
GOOGLE_CLIENT_SECRET="your_client_secret_here"

# Application Settings
LOG_LEVEL="INFO"
EOF

# main.js (Electron Main Process)
cat <<EOF > main.js
// Electron Main Process Entry Point
// This file will launch the app window and the Python backend.
console.log("main.js loaded");
EOF

# frontend/index.html
cat <<EOF > frontend/index.html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'">
    <title>Aperture</title>
    <link rel="stylesheet" href="./assets/style.css">
</head>
<body>
    <h1>Welcome to Aperture</h1>
    <p>Your personal oracle is warming up...</p>
    <script src="./js/renderer.js"></script>
</body>
</html>
EOF

# frontend/js/renderer.js
cat <<EOF > frontend/js/renderer.js
// Frontend UI Logic
// This file will handle user interactions and fetch requests to the backend.
console.log("renderer.js loaded");
EOF

# package.json (Initialize if it doesn't exist)
if [ ! -f package.json ]; then
    npm init -y
    # Add a main entry point for Electron
    sed -i 's/"main": "index.js"/"main": "main.js"/' package.json
fi

echo "✅ Project structure scaffolded successfully!"
echo "➡️ Next steps: run 'npm install' and start building!"