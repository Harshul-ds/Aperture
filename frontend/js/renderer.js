// frontend/js/renderer.js (Final Proactive Version)

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    const navSearch = document.getElementById('nav-search');
    const navJobs = document.getElementById('nav-jobs');
    const searchPageContainer = document.getElementById('search-page-container');
    const jobTrackerContainer = document.getElementById('job-tracker-container');
    const logOutput = document.getElementById('log-output');
    const ingestButton = document.getElementById('ingest-button');

    // --- State ---
    let searchTimeout;

    // --- Live Log Functionality ---
    const connectToLogStream = () => {
        logOutput.textContent = 'Attempting to connect to backend log stream...\n';
        const socket = new WebSocket('ws://127.0.0.1:8000/log/ws');

        socket.onopen = () => {
            logOutput.textContent = '✅ Backend log stream connected.\n\n';
            // --- KEY FIX: Once connected, proactively fetch data ---
            fetchAndRenderJobs();
        };

        socket.onmessage = (event) => {
            logOutput.textContent += event.data + '\n';
            logOutput.scrollTop = logOutput.scrollHeight;
        };

        socket.onclose = (event) => {
            logOutput.textContent += '\n--- Log stream disconnected. Retrying in 3 seconds... ---\n';
            setTimeout(connectToLogStream, 3000);
        };

        socket.onerror = (error) => {
            console.error('WebSocket Error:', error);
        };
    };

    // --- Page Navigation & Data Fetching ---
    function switchToSearchView() {
        searchPageContainer.classList.remove('hidden');
        jobTrackerContainer.classList.add('hidden');
        navSearch.classList.add('active');
        navJobs.classList.remove('active');
    }

    async function switchToJobsView() {
        searchPageContainer.classList.add('hidden');
        jobTrackerContainer.classList.remove('hidden');
        navSearch.classList.remove('active');
        navJobs.classList.add('active');
        await fetchAndRenderJobs();
    }

    async function fetchAndRenderJobs() {
        try {
            jobTrackerContainer.innerHTML = '<p>Loading job applications...</p>';
            const response = await fetch('http://127.0.0.1:8000/jobs/');
            if (!response.ok) throw new Error(`Server responded with ${response.status}`);
            const data = await response.json();
            if (data.status === 'success') {
                renderJobBoard(data.results);
            } else {
                jobTrackerContainer.innerHTML = '<p>Could not load job applications.</p>';
            }
        } catch (error) {
            console.error('Error fetching job applications:', error);
            jobTrackerContainer.innerHTML = `<p style="color:red;">Error loading job applications: ${error.message}</p>`;
        }
    }

    const handleIngestClick = async () => {
        ingestButton.textContent = 'Syncing...';
        ingestButton.disabled = true;
        logOutput.textContent += 'INFO: Manual ingestion triggered from UI.\n';
        try {
            await fetch('http://127.0.0.1:8000/ingest/gmail', { method: 'POST' });
        } catch (error) {
            console.error('Failed to trigger ingestion:', error);
            logOutput.textContent += 'ERROR: Failed to trigger ingestion.\n';
        }
        // After ingestion is triggered, wait a bit then refresh the UI
        setTimeout(() => {
            ingestButton.textContent = 'Sync New Emails';
            ingestButton.disabled = false;
            fetchAndRenderJobs(); // Refresh the job board
        }, 5000); // 5 second delay to allow backend to process
    };

    // ... your other functions (handleSearch, renderSearchResults, renderJobBoard) ...

    // --- Event Listeners & Initial Calls ---
    searchInput.addEventListener('input', handleSearch);
    navSearch.addEventListener('click', switchToSearchView);
    navJobs.addEventListener('click', switchToJobsView);
    ingestButton.addEventListener('click', handleIngestClick);

    connectToLogStream();
});