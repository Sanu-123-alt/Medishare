// Function to switch between tabs
function switchTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });

    // Remove active class from all tabs
    document.querySelectorAll('.nav-link').forEach(tab => {
        tab.classList.remove('active');
    });

    // Show the selected tab content
    document.getElementById(tabId).style.display = 'block';

    // Add active class to the clicked tab
    document.querySelector(`[onclick="switchTab('${tabId}')"]`).classList.add('active');
}

// Function to show modal
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        // Clear any previous form data
        const form = modal.querySelector('form');
        if (form) form.reset();
        
        // Show the modal
        modal.style.display = 'block';
    }
}

// Function to close modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Function to handle doctor form submission
function submitDoctorForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch('/hospital/add-doctor/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close the modal and refresh the page
            closeModal('doctorModal');
            location.reload();
        } else {
            // Show error message
            alert(data.message || 'An error occurred while adding the doctor.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the doctor.');
    });
}

// Function to handle department form submission
function submitDepartmentForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch('/hospital/add-department/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close the modal and refresh the page
            closeModal('departmentModal');
            location.reload();
        } else {
            // Show error message
            alert(data.message || 'An error occurred while adding the department.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the department.');
    });
}

// Function to edit doctor
function editDoctor(doctorId) {
    fetch(`/hospital/doctor/${doctorId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Populate the form with doctor data
                const form = document.getElementById('doctorForm');
                for (const [key, value] of Object.entries(data.doctor)) {
                    const input = form.querySelector(`[name=${key}]`);
                    if (input) input.value = value;
                }
                showModal('doctorModal');
            } else {
                alert('Error loading doctor data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while loading doctor data');
        });
}

// Function to delete doctor
function deleteDoctor(doctorId) {
    if (confirm('Are you sure you want to delete this doctor?')) {
        fetch(`/hospital/doctor/${doctorId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'An error occurred while deleting the doctor');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the doctor');
        });
    }
}

// Function to edit department
function editDepartment(deptId) {
    fetch(`/hospital/department/${deptId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Populate the form with department data
                const form = document.getElementById('departmentForm');
                for (const [key, value] of Object.entries(data.department)) {
                    const input = form.querySelector(`[name=${key}]`);
                    if (input) input.value = value;
                }
                showModal('departmentModal');
            } else {
                alert('Error loading department data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while loading department data');
        });
}

// Function to delete department
function deleteDepartment(deptId) {
    if (confirm('Are you sure you want to delete this department?')) {
        fetch(`/hospital/department/${deptId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'An error occurred while deleting the department');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the department');
        });
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize when the page loads
// Function to edit service
function editService(serviceId) {
    fetch(`/hospital/service/${serviceId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Populate the form with service data
                const form = document.getElementById('serviceForm');
                for (const [key, value] of Object.entries(data.service)) {
                    const input = form.querySelector(`[name=${key}]`);
                    if (input) input.value = value;
                }
                showModal('serviceModal');
            } else {
                alert('Error loading service data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while loading service data');
        });
}

// Function to delete service
function deleteService(serviceId) {
    if (confirm('Are you sure you want to delete this service?')) {
        fetch(`/hospital/service/${serviceId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'An error occurred while deleting the service');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the service');
        });
    }
}

// Function to edit achievement
function editAchievement(achievementId) {
    fetch(`/hospital/achievement/${achievementId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Populate the form with achievement data
                const form = document.getElementById('achievementForm');
                for (const [key, value] of Object.entries(data.achievement)) {
                    const input = form.querySelector(`[name=${key}]`);
                    if (input) input.value = value;
                }
                showModal('achievementModal');
            } else {
                alert('Error loading achievement data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while loading achievement data');
        });
}

// Function to delete achievement
function deleteAchievement(achievementId) {
    if (confirm('Are you sure you want to delete this achievement?')) {
        fetch(`/hospital/achievement/${achievementId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'An error occurred while deleting the achievement');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the achievement');
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Set initial active tab
    switchTab('doctors');

    // Set up form submission handlers
    const doctorForm = document.getElementById('doctorForm');
    if (doctorForm) {
        doctorForm.addEventListener('submit', submitDoctorForm);
    }

    const departmentForm = document.getElementById('departmentForm');
    if (departmentForm) {
        departmentForm.addEventListener('submit', submitDepartmentForm);
    }
});