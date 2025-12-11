// Hero Chart
function createHeroChart() {
    const ctx = document.getElementById('heroChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Health Score',
                data: [85, 87, 83, 89, 92, 95],
                borderColor: '#06b6d4',
                backgroundColor: 'rgba(6, 182, 212, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#06b6d4',
                pointBorderColor: '#fff',
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 70,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#06b6d4',
                    bodyColor: '#fff',
                    borderColor: 'rgba(6, 182, 212, 0.2)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false
                }
            }
        }
    });
}

// Initialize chart when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    createHeroChart();
});

// Modal Functions
function showLoginModal() {
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
}

function showUploadModal() {
    const uploadModal = new bootstrap.Modal(document.getElementById('uploadModal'));
    uploadModal.show();
}

function showSuccessModal() {
    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
    successModal.show();
}

// Password Toggle
function togglePassword(button) {
    const input = button.parentElement.querySelector('input');
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Scroll to Section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Toast Notifications
function showToast(type, message) {
    const toastContainer = document.querySelector('.toast-container');
    
    const toast = document.createElement('div');
    toast.className = `custom-toast toast-${type} mb-3`;
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas ${type === 'success' ? 'fa-check-circle text-success' : 
                          type === 'error' ? 'fa-exclamation-circle text-danger' : 
                          'fa-exclamation-triangle text-warning'} me-2"></i>
            <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
            <small>Just now</small>
            <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Upload Area Functionality
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const uploadProgress = document.getElementById('uploadProgress');
const progressBar = document.querySelector('.progress-bar');
const uploadBtn = document.getElementById('uploadBtn');

if (uploadArea) {
    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        uploadArea.classList.add('dragover');
    }

    function unhighlight() {
        uploadArea.classList.remove('dragover');
    }

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            fileList.innerHTML = '';
            Array.from(files).forEach(file => {
                addFileToList(file);
            });
            showToast('success', `${files.length} file(s) ready for upload`);
        }
    }

    function addFileToList(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        // Determine file icon based on type
        let iconClass = 'fa-file';
        if (file.type.includes('pdf')) iconClass = 'fa-file-pdf';
        else if (file.type.includes('image')) iconClass = 'fa-file-image';
        else if (file.type.includes('word')) iconClass = 'fa-file-word';
        else if (file.type.includes('xml')) iconClass = 'fa-file-code';
        
        fileItem.innerHTML = `
            <div class="file-info">
                <div class="file-icon">
                    <i class="fas ${iconClass}"></i>
                </div>
                <div class="file-details">
                    <h6>${file.name}</h6>
                    <span>${formatFileSize(file.size)}</span>
                </div>
            </div>
            <button class="btn btn-sm btn-outline-danger" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        fileList.appendChild(fileItem);
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Custom encryption key toggle
const customRadio = document.getElementById('custom');
const autoRadio = document.getElementById('auto');
const customKeyInput = document.getElementById('customKeyInput');

if (customRadio && autoRadio) {
    customRadio.addEventListener('change', function() {
        if (this.checked) {
            customKeyInput.style.display = 'block';
        }
    });

    autoRadio.addEventListener('change', function() {
        if (this.checked) {
            customKeyInput.style.display = 'none';
        }
    });
}

// Generate random encryption key
function generateKey() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+';
    let key = '';
    for (let i = 0; i < 24; i++) {
        key += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    const keyInput = document.querySelector('#customKeyInput input');
    if (keyInput) {
        keyInput.value = key;
        updateKeyStrength(key);
    }
}

// Update key strength indicator
function updateKeyStrength(key) {
    const strengthSpan = document.getElementById('keyStrength');
    if (!strengthSpan) return;
    
    let strength = 'Weak';
    let color = '#ef4444';
    
    if (key.length >= 16) {
        const hasUpper = /[A-Z]/.test(key);
        const hasLower = /[a-z]/.test(key);
        const hasNumber = /[0-9]/.test(key);
        const hasSpecial = /[^A-Za-z0-9]/.test(key);
        
        const score = [hasUpper, hasLower, hasNumber, hasSpecial].filter(Boolean).length;
        
        if (score === 4 && key.length >= 20) {
            strength = 'Very Strong';
            color = '#10b981';
        } else if (score >= 3 && key.length >= 16) {
            strength = 'Strong';
            color = '#059669';
        } else if (score >= 2) {
            strength = 'Moderate';
            color = '#f59e0b';
        }
    }
    
    strengthSpan.textContent = strength;
    strengthSpan.style.color = color;
}

// Listen for key input
const keyInput = document.querySelector('#customKeyInput input');
if (keyInput) {
    keyInput.addEventListener('input', function() {
        updateKeyStrength(this.value);
    });
}

// Simulate file upload
function startUpload() {
    const fileItems = fileList.querySelectorAll('.file-item');
    
    if (fileItems.length === 0) {
        showToast('warning', 'Please select files to upload');
        return;
    }
    
    // Check if custom key is selected but empty
    if (customRadio.checked) {
        const keyInput = document.querySelector('#customKeyInput input');
        if (!keyInput.value || keyInput.value.length < 16) {
            showToast('error', 'Please enter a valid encryption key (min 16 characters)');
            return;
        }
    }
    
    // Show upload progress
    uploadArea.style.display = 'none';
    uploadProgress.style.display = 'block';
    fileList.style.display = 'none';
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="loading-spinner me-2"></span> Uploading...';
    
    // Simulate progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            
            // Show encryption animation
            progressBar.style.width = '100%';
            uploadBtn.innerHTML = '<span class="loading-spinner me-2"></span> Encrypting...';
            
            setTimeout(() => {
                // Show success modal
                const uploadModal = bootstrap.Modal.getInstance(document.getElementById('uploadModal'));
                uploadModal.hide();
                
                setTimeout(() => {
                    showSuccessModal();
                    
                    // Reset upload form
                    setTimeout(() => {
                        uploadArea.style.display = 'block';
                        uploadProgress.style.display = 'none';
                        fileList.style.display = 'block';
                        fileList.innerHTML = '';
                        uploadBtn.disabled = false;
                        uploadBtn.innerHTML = '<i class="fas fa-upload"></i> Upload Securely';
                        progressBar.style.width = '0%';
                    }, 1000);
                }, 500);
            }, 1500);
        } else {
            progressBar.style.width = `${progress}%`;
        }
    }, 200);
}

// Login form submission
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Simulate login process
        const loginBtn = this.querySelector('button[type="submit"]');
        loginBtn.innerHTML = '<span class="loading-spinner me-2"></span> Authenticating...';
        loginBtn.disabled = true;
        
        setTimeout(() => {
            // Close modal
            const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            loginModal.hide();
            
            // Show success toast
            showToast('success', 'Login successful! Welcome back.');
            
            // Reset form
            loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Secure Login';
            loginBtn.disabled = false;
            loginForm.reset();
        }, 2000);
    });
}