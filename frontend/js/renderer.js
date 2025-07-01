document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    const navSearch = document.getElementById('nav-search');
    const navJobs = document.getElementById('nav-jobs');
    const searchPageContainer = document.getElementById('search-page-container');
    const jobTrackerContainer = document.getElementById('job-tracker-container');

    // --- State ---
    let searchTimeout;

    // --- Page Navigation ---
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

    // --- Search Functionality ---
    function handleSearch() {
        clearTimeout(searchTimeout);
        const query = searchInput.value;

        if (query.length > 2) {
            searchTimeout = setTimeout(() => {
                fetch(`http://127.0.0.1:8000/search/?query=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => renderSearchResults(data))
                    .catch(error => {
                        console.error('Error fetching search results:', error);
                        resultsContainer.innerHTML = '<p>Error loading results.</p>';
                    });
            }, 300);
        } else {
            resultsContainer.innerHTML = '';
        }
    }

    function renderSearchResults(data) {
        resultsContainer.innerHTML = '';
        if (data.results && data.results.length > 0) {
            data.results.forEach(item => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';

                const header = document.createElement('div');
                header.className = 'result-header';

                const sender = document.createElement('div');
                sender.className = 'result-sender';
                sender.textContent = item.sender;

                const categoryTag = document.createElement('span');
                categoryTag.className = `category-tag category-${item.category.toLowerCase().replace(/\s+/g, '-')}`;
                categoryTag.textContent = item.category;

                const relevance = document.createElement('div');
                relevance.className = 'result-relevance';
                relevance.textContent = `Relevance: ${item.relevance_score}`;

                header.appendChild(sender);
                header.appendChild(categoryTag);
                header.appendChild(relevance);

                const subject = document.createElement('div');
                subject.className = 'result-subject';
                subject.textContent = item.has_attachment ? `${item.subject} 📎` : item.subject;

                const preview = document.createElement('div');
                preview.className = 'result-preview';
                preview.textContent = item.preview;

                resultItem.appendChild(header);
                resultItem.appendChild(subject);
                resultItem.appendChild(preview);
                resultsContainer.appendChild(resultItem);
            });
        } else {
            resultsContainer.innerHTML = '<p>No results found.</p>';
        }
    }

    // --- Job Tracker Functionality ---
    async function fetchAndRenderJobs() {
        try {
            jobTrackerContainer.innerHTML = '<p>Loading job applications...</p>';
            const response = await fetch('http://127.0.0.1:8000/jobs/');
            const data = await response.json();
            if (data.status === 'success') {
                renderJobBoard(data.results);
            } else {
                jobTrackerContainer.innerHTML = '<p>Could not load job applications.</p>';
            }
        } catch (error) {
            console.error('Error fetching job applications:', error);
            jobTrackerContainer.innerHTML = '<p>Error loading job applications.</p>';
        }
    }

    function renderJobBoard(jobs) {
        jobTrackerContainer.innerHTML = '';

        const statuses = ['Applied', 'Interview', 'Offer', 'Rejected'];
        const jobsByStatus = statuses.reduce((acc, status) => {
            acc[status] = jobs.filter(job => job.status === status);
            return acc;
        }, {});

        statuses.forEach(status => {
            const column = document.createElement('div');
            column.className = 'job-status-column';

            const title = document.createElement('h2');
            title.textContent = `${status} (${jobsByStatus[status].length})`;
            column.appendChild(title);

            jobsByStatus[status].forEach(job => {
                const card = document.createElement('div');
                card.className = 'job-card';

                const company = document.createElement('div');
                company.className = 'job-card-company';
                company.textContent = job.company || 'Unknown Company';

                const subject = document.createElement('div');
                subject.className = 'job-card-subject';
                subject.textContent = job.subject;

                card.appendChild(company);
                card.appendChild(subject);
                column.appendChild(card);
            });

            jobTrackerContainer.appendChild(column);
        });
    }

    // --- Event Listeners ---
    searchInput.addEventListener('input', handleSearch);
    navSearch.addEventListener('click', switchToSearchView);
    navJobs.addEventListener('click', switchToJobsView);
});
