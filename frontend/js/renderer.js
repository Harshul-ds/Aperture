// frontend/js/renderer.js

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    const API_BASE_URL = 'http://127.0.0.1:8000'; // Default FastAPI server address

    // --- Function to perform the search ---
    async function performSearch(query) {
        if (!query) {
            resultsContainer.innerHTML = ''; // Clear results if query is empty
            return;
        }

        // Display a loading message
        resultsContainer.innerHTML = '<p>Searching...</p>';

        try {
            // Construct the full URL with the URL-encoded query parameter
            const url = new URL(`${API_BASE_URL}/search/`);
            url.searchParams.append('q', query);

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            console.error('Fetch error:', error);
            resultsContainer.innerHTML = `<p class="error">Failed to fetch search results. Is the backend running?</p>`;
        }
    }

    // --- Function to display the results in the DOM ---
    function displayResults(data) {
        // Clear previous results or loading message
        resultsContainer.innerHTML = '';

        if (data.status === 'error' || !data.results || data.results.length === 0) {
            resultsContainer.innerHTML = '<p>No results found.</p>';
            return;
        }

        const resultList = document.createElement('ul');
        resultList.className = 'results-list';

        data.results.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'result-item';

            // Sanitize content before inserting to prevent XSS
            const sender = document.createElement('span');
            sender.className = 'sender';
            sender.textContent = item.sender;

            const relevance = document.createElement('span');
            relevance.className = 'relevance';
            relevance.textContent = `Relevance: ${item.relevance_score}`;

            const header = document.createElement('div');
            header.className = 'result-header';
            header.appendChild(sender);
            header.appendChild(relevance);

            const subject = document.createElement('div');
            subject.className = 'result-subject';
            subject.textContent = item.subject;

            const preview = document.createElement('div');
            preview.className = 'result-preview';
            preview.textContent = item.preview;

            listItem.appendChild(header);
            listItem.appendChild(subject);
            listItem.appendChild(preview);
            
            resultList.appendChild(listItem);
        });

        resultsContainer.appendChild(resultList);
    }

    // --- Add event listener to the search input ---
    searchInput.addEventListener('keyup', (event) => {
        // Trigger search on "Enter" key
        if (event.key === 'Enter') {
            performSearch(searchInput.value.trim());
        }
    });
});
