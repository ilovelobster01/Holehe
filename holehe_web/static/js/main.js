let currentSearchId = null;
let progressInterval = null;

document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    if (!email) {
        showError('Please enter an email address');
        return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('Please enter a valid email address');
        return;
    }

    startSearch(email);
});

function startSearch(email) {
    // Reset UI
    hideError();
    hideResults();
    showProgress();

    const searchBtn = document.getElementById('searchBtn');
    searchBtn.disabled = true;
    searchBtn.textContent = '🔄 Searching...';

    // Start search
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `email=${encodeURIComponent(email)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }

        currentSearchId = data.search_id;
        checkProgress();
    })
    .catch(error => {
        showError('Failed to start search: ' + error.message);
        resetSearchButton();
    });
}

function checkProgress() {
    if (!currentSearchId) return;

    fetch(`/status/${currentSearchId}`)
    .then(response => response.json())
    .then(data => {
        updateProgress(data.progress || 0, data.message || 'Searching...');

        if (data.status === 'completed') {
            loadResults();
        } else if (data.status === 'error') {
            showError(data.message || 'Search failed');
            resetSearchButton();
        } else {
            // Continue checking
            setTimeout(checkProgress, 1000);
        }
    })
    .catch(error => {
        showError('Failed to check progress: ' + error.message);
        resetSearchButton();
    });
}

function loadResults() {
    fetch(`/results/${currentSearchId}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }

        displayResults(data);
        hideProgress();
        resetSearchButton();
    })
    .catch(error => {
        showError('Failed to load results: ' + error.message);
        resetSearchButton();
    });
}

function displayResults(data) {
    const summaryDiv = document.getElementById('resultsSummary');
    const profilesDiv = document.getElementById('profilesList');
    const resultsActions = document.getElementById('resultsActions');
    const filterSection = document.getElementById('filterSection');
    const filterStats = document.getElementById('filterStats');
    const downloadBtnTop = document.getElementById('downloadBtnTop');
    const downloadBtnBottom = document.getElementById('downloadBtnBottom');

    // Show results actions and filter section
    resultsActions.style.display = 'flex';
    filterSection.style.display = 'block';

    // Summary
    summaryDiv.innerHTML = `
        <div class="summary-item">
            <strong>Email Address:</strong>
            <span>${data.email}</span>
        </div>
        <div class="summary-item">
            <strong>Total Sites Checked:</strong>
            <span>${data.total_sites}</span>
        </div>
        <div class="summary-item">
            <strong>Search Time:</strong>
            <span>${new Date(data.search_time).toLocaleString()}</span>
        </div>
    `;

    // Filter stats
    filterStats.innerHTML = `
        <div class="stat-item stat-found">
            ✅ <span>${data.found_count || 0} Found</span>
        </div>
        <div class="stat-item stat-not-found">
            ❌ <span>${data.not_found_count || 0} Not Found</span>
        </div>
        <div class="stat-item stat-rate-limited">
            ⚠️ <span>${data.rate_limited_count || 0} Rate Limited</span>
        </div>
        <div class="stat-item stat-error">
            🚫 <span>${data.error_count || 0} Errors</span>
        </div>
    `;

    // Combine all profiles with their types
    let allProfiles = [];

    // Add found profiles
    if (data.found_profiles) {
        allProfiles = allProfiles.concat(data.found_profiles.map(profile => ({
            ...profile,
            type: 'found',
            displayStatus: 'Found'
        })));
    }

    // Add not found profiles
    if (data.not_found_profiles) {
        allProfiles = allProfiles.concat(data.not_found_profiles.map(profile => ({
            ...profile,
            type: 'not_found',
            displayStatus: 'Not Found'
        })));
    }

    // Add rate limited profiles
    if (data.rate_limited_profiles) {
        allProfiles = allProfiles.concat(data.rate_limited_profiles.map(profile => ({
            ...profile,
            type: 'rate_limited',
            displayStatus: profile.reason || 'Rate Limited'
        })));
    }

    // Add error profiles
    if (data.error_profiles) {
        allProfiles = allProfiles.concat(data.error_profiles.map(profile => ({
            ...profile,
            type: 'error',
            displayStatus: profile.reason || 'Error'
        })));
    }

    // Sort profiles by site name
    allProfiles.sort((a, b) => a.site.localeCompare(b.site));

    // Display profiles
    if (allProfiles.length > 0) {
        profilesDiv.innerHTML = allProfiles.map(profile => {
            let additionalInfo = '';
            if (profile.emailrecovery) {
                additionalInfo += `<div class="profile-additional-info"><strong>Email Recovery:</strong> ${profile.emailrecovery}</div>`;
            }
            if (profile.phoneNumber) {
                additionalInfo += `<div class="profile-additional-info"><strong>Phone:</strong> ${profile.phoneNumber}</div>`;
            }
            if (profile.others) {
                for (const [key, value] of Object.entries(profile.others)) {
                    additionalInfo += `<div class="profile-additional-info"><strong>${key}:</strong> ${value}</div>`;
                }
            }

            return `
                <div class="profile-item ${profile.type}" data-type="${profile.type}">
                    <div style="flex-grow: 1;">
                        <div class="profile-name">
                            ${profile.site}
                            <span class="profile-status status-${profile.type}">${profile.displayStatus}</span>
                        </div>
                        <div class="profile-domain">${profile.domain}</div>
                        ${additionalInfo}
                    </div>
                    <div style="color: #666; font-size: 0.9em;">
                        ${profile.method || 'Unknown method'}
                    </div>
                </div>
            `;
        }).join('');

        // Show download buttons only if there are found profiles
        const hasFoundProfiles = data.found_count > 0;
        downloadBtnTop.style.display = hasFoundProfiles ? 'inline-block' : 'none';
        downloadBtnBottom.style.display = hasFoundProfiles ? 'inline-block' : 'none';
        downloadBtnTop.onclick = () => downloadPDF();
        downloadBtnBottom.onclick = () => downloadPDF();

        // Set up filter functionality
        setupFilters();

    } else {
        profilesDiv.innerHTML = '<div class="no-results">No results found for this email address.</div>';
        downloadBtnTop.style.display = 'none';
        downloadBtnBottom.style.display = 'none';
    }

    showResults();
    showBackToTopButton();
}

function downloadPDF() {
    if (currentSearchId) {
        window.open(`/download/${currentSearchId}`, '_blank');
    }
}

function showProgress() {
    document.getElementById('progressContainer').style.display = 'block';
}

function hideProgress() {
    document.getElementById('progressContainer').style.display = 'none';
}

function updateProgress(percent, message) {
    document.getElementById('progressFill').style.width = percent + '%';
    document.getElementById('progressText').textContent = message;
}

function showResults() {
    document.getElementById('resultsContainer').style.display = 'block';
}

function hideResults() {
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('resultsActions').style.display = 'none';
    document.getElementById('filterSection').style.display = 'none';
    hideBackToTopButton();
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function resetSearchButton() {
    const searchBtn = document.getElementById('searchBtn');
    searchBtn.disabled = false;
    searchBtn.textContent = '🔍 Check Email Accounts';
    hideProgress();
}

function resetSearch() {
    // Clear current search
    currentSearchId = null;

    // Clear input
    document.getElementById('email').value = '';

    // Hide results and progress
    hideResults();
    hideProgress();
    hideError();

    // Reset search button
    resetSearchButton();

    // Scroll to top
    scrollToTop();
}

function showBackToTopButton() {
    document.getElementById('backToTopBtn').style.display = 'block';
}

function hideBackToTopButton() {
    document.getElementById('backToTopBtn').style.display = 'none';
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function setupFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');

    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Get filter type
            const filterType = this.getAttribute('data-filter');

            // Apply filter
            applyFilter(filterType);
        });
    });
}

function applyFilter(filterType) {
    const profileItems = document.querySelectorAll('.profile-item');

    profileItems.forEach(item => {
        if (filterType === 'all') {
            item.classList.remove('hidden');
        } else {
            const itemType = item.getAttribute('data-type');
            if (itemType === filterType) {
                item.classList.remove('hidden');
            } else {
                item.classList.add('hidden');
            }
        }
    });
}

// Event listeners for new buttons
document.getElementById('resetBtn').addEventListener('click', resetSearch);
document.getElementById('backToTopBtn').addEventListener('click', scrollToTop);

// Show/hide back to top button based on scroll
window.addEventListener('scroll', function() {
    const backToTopBtn = document.getElementById('backToTopBtn');
    if (window.pageYOffset > 300) {
        backToTopBtn.style.display = 'block';
    } else if (!document.getElementById('resultsContainer').style.display ||
               document.getElementById('resultsContainer').style.display === 'none') {
        backToTopBtn.style.display = 'none';
    }
});
