// main.js - Electron Main Process

const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let pyProcess = null;

// --- Function to Start the FastAPI Backend ---
function startPythonBackend() {
    // Run the backend as a module to ensure correct pathing
    pyProcess = spawn('python3', ['-m', 'backend.main'], {
        cwd: __dirname, // Set the working directory to the project root
    });

    pyProcess.stdout.on('data', (data) => {
        console.log(`Python stdout: ${data}`);
    });

    pyProcess.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data}`);
    });

    pyProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
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
