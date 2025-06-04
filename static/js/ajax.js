// AJAX utility functions
function ajaxRequest(url, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(xhr.response ? JSON.parse(xhr.response) : null);
            } else {
                reject(new Error(`Request failed: ${xhr.status}`));
            }
        };

        xhr.onerror = () => reject(new Error('Network error'));
        
        xhr.send(data ? JSON.stringify(data) : null);
    });
}

// Medicine search functionality
function searchMedicines() {
    const searchTerm = document.getElementById('medicine-search').value;
    
    if (searchTerm.length < 3) return; // Don't search for short terms
    
    ajaxRequest('/api/medicines', 'GET')
        .then(medicines => {
            const resultsContainer = document.getElementById('medicine-results');
            if (!resultsContainer) return;
            
            if (medicines.length === 0) {
                resultsContainer.innerHTML = '<p>No medicines found</p>';
                return;
            }
            
            const html = medicines.map(medicine => `
                <div class="medicine-item">
                    <h3>${medicine.name}</h3>
                    <p>Quantity: ${medicine.quantity} ${medicine.quantity_unit}</p>
                    <p>Expiry: ${medicine.expiry_date}</p>
                    <button onclick="viewMedicine(${medicine.id})">View Details</button>
                </div>
            `).join('');
            
            resultsContainer.innerHTML = html;
        })
        .catch(error => console.error('Error searching medicines:', error));
}

// View medicine details
function viewMedicine(id) {
    ajaxRequest(`/api/medicine/${id}`, 'GET')
        .then(medicine => {
            const modal = document.getElementById('medicine-modal');
            if (!modal) return;
            
            modal.innerHTML = `
                <div class="modal-content">
                    <h2>${medicine.name}</h2>
                    <p>Quantity: ${medicine.quantity} ${medicine.quantity_unit}</p>
                    <p>Expiry: ${medicine.expiry_date}</p>
                    <p>Donor: ${medicine.donor_name}</p>
                    <p>Contact: ${medicine.donor_email}</p>
                    <p>Description: ${medicine.description}</p>
                    ${medicine.image_path ? `<img src="${medicine.image_path}" alt="${medicine.name}">` : ''}
                    <button onclick="closeModal()">Close</button>
                </div>
            `;
            
            modal.style.display = 'block';
        })
        .catch(error => console.error('Error viewing medicine:', error));
}

// Get user activities
function loadActivities() {
    ajaxRequest('/api/activities', 'GET')
        .then(activities => {
            const activitiesContainer = document.getElementById('user-activities');
            if (!activitiesContainer) return;
            
            if (activities.length === 0) {
                activitiesContainer.innerHTML = '<p>No recent activities</p>';
                return;
            }
            
            const html = activities.map(activity => `
                <div class="activity-item">
                    <p>${activity.action}</p>
                    <small>${activity.created_at}</small>
                </div>
            `).join('');
            
            activitiesContainer.innerHTML = html;
        })
        .catch(error => console.error('Error loading activities:', error));
}

// Utility function to close modal
function closeModal() {
    const modal = document.getElementById('medicine-modal');
    if (modal) modal.style.display = 'none';
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('medicine-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchMedicines, 300));
    }
    
    loadActivities();
});

// Debounce function to prevent too many requests
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
