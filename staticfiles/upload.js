const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('uploadBrowseBtn'); // Changed to uploadBrowseBtn

// CSRF token for Django
function getCSRFToken() {
    const cookieValue = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    return cookieValue;
}

if (browseBtn) {
    browseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const loggedIn = browseBtn.getAttribute("data-logged-in") === "true";
        if (loggedIn && fileInput) {
            fileInput.click();
        } else {
            window.location.href = "/user/choice_login/?next=/user/upload_record/";
        }
    });
}

if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            handleFiles(files);
            fileInput.value = '';
        }
    });
}

if (uploadArea) {
    const loggedIn = uploadArea.getAttribute("data-logged-in") === "true";
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--neon-blue)';
        uploadArea.style.backgroundColor = 'rgba(0, 247, 255, 0.1)';
        uploadArea.querySelector('i').style.color = 'var(--neon-blue)';
    });
    uploadArea.addEventListener('dragleave', resetUploadArea);
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        resetUploadArea();
        if (loggedIn && fileInput) {
            fileInput.files = e.dataTransfer.files;
            handleFiles(fileInput.files);
        } else {
            window.location.href = "/user/choice_login/?next=/user/upload_record/";
        }
    });
}

function resetUploadArea() {
    if (!uploadArea) return;
    uploadArea.style.borderColor = 'var(--glass-border)';
    uploadArea.style.backgroundColor = 'rgba(255, 255, 255, 0.03)';
    uploadArea.querySelector('i').style.color = 'var(--neon-blue)';
}

function handleFiles(files) {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'application/dicom', 'application/xml', 'application/hl7'];
    for (let file of files) {
        if (!allowedTypes.includes(file.type)) {
            showAlert(`Invalid file type for ${file.name}. Supported: PDF, JPG/PNG, DICOM, HL7, XML.`, 'danger');
            continue;
        }
        const formData = new FormData();
        formData.append('file', file);
        fetch('/user/upload_record/', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': getCSRFToken() },
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            const fileName = file.name;
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            showAlert(`${fileName} (${fileSize} MB) uploaded successfully! ${data.message || 'Our AI is now processing your document.'}`, 'success');
        })
        .catch(error => showAlert(`Upload failed for ${file.name}: ${error.message}`, 'danger'));
    }
}

function showAlert(message, type='success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} mt-3`;
    alertDiv.innerHTML = message;
    alertDiv.style.textAlign = 'center';
    alertDiv.style.fontSize = '0.9rem';
    if (uploadArea) {
        uploadArea.appendChild(alertDiv);
    }
    setTimeout(() => alertDiv.remove(), 4000);
}

// REMOVE ALL PROBLEMATIC CODE - DELETE EVERYTHING BELOW THIS LINE