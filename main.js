// main.js - Electron Main Process

const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

let pyProcess = null;

// Resolve a python interpreter in a cross-platform way
function resolvePythonExecutable() {
    // 1. Explicit override
    if (process.env.PYTHON_PATH && fs.existsSync(process.env.PYTHON_PATH)) {
        return process.env.PYTHON_PATH;
    }

    // 2. Virtual-env detection
    if (process.env.VIRTUAL_ENV) {
        const candidate = process.platform === 'win32'
            ? path.join(process.env.VIRTUAL_ENV, 'Scripts', 'python.exe')
            : path.join(process.env.VIRTUAL_ENV, 'bin', 'python3');
        if (fs.existsSync(candidate)) {
            return candidate;
        }
    }

    // 3. Fallback to system python (relies on PATH)
    return process.platform === 'win32' ? 'python' : 'python3';
}

// --- Function to Start the FastAPI Backend ---
function startPythonBackend() {
    console.log("Attempting to start Uvicorn server...");

        const pythonExecutable = resolvePythonExecutable();
    
    // Command to run: uvicorn. The arguments tell it which app to run and how.
    // This is the command-line equivalent of 'uvicorn backend.main:app --host 127.0.0.1 --port 8000'
    pyProcess = spawn(pythonExecutable, [
        '-m', 'uvicorn', 
        'backend.main:app', 
        '--host', '127.0.0.1', 
        '--port', '8000'
    ], {
        cwd: __dirname,
        env: { ...process.env, "PYTHONWARNINGS": "ignore" }
    });

    pyProcess.stdout.on('data', (data) => {
        // We use .trim() to clean up extra newlines from the buffer
        console.log(`Python stdout: ${data.toString().trim()}`);
    });

    pyProcess.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data.toString().trim()}`);
    });

    pyProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
    });

    pyProcess.on('error', (err) => {
        console.error('Failed to start Python subprocess.', err);
    });
}

// --- Function to Create the Electron Window ---
function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            // Correctly point to the preload script
            preload: path.join(__dirname, 'frontend', 'preload.js'),
            // Security best practice: contextIsolation is true by default
            contextIsolation: true,
            // For renderer to access node modules (if needed, but prefer preload)
            nodeIntegration: false,
        },
    });

    // Load the main HTML file for the UI
    win.loadFile(path.join(__dirname, 'frontend', 'index.html'));

    // Optional: Open DevTools for debugging
    // win.webContents.openDevTools();
}

// --- App Lifecycle Events ---

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
app.whenReady().then(() => {
    console.log('App is ready, starting backend...');
    startPythonBackend();
    createWindow();

    app.on('activate', () => {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

// Quit when all windows are closed, except on macOS.
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// On app quit, kill the python backend server
app.on('will-quit', () => {
    if (pyProcess) {
        pyProcess.kill();
    }
});
