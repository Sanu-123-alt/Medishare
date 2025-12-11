// ======================== AOS ========================
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: false,
    offset: 80
});

// ======================== Particles.js ========================
particlesJS('particles-js', {
    "particles": {
        "number": { "value": 80, "density": { "enable": true, "value_area": 800 } },
        "color": { "value": "#00c6ff" },
        "shape": { "type": "circle", "stroke": { "width": 0, "color": "#000000" } },
        "opacity": { "value": 0.5, "random": true, "anim": { "enable": true, "speed": 1, "opacity_min": 0.1, "sync": false } },
        "size": { "value": 3, "random": true, "anim": { "enable": false, "speed": 40, "size_min": 0.1, "sync": false } },
        "line_linked": { "enable": true, "distance": 150, "color": "#00c6ff", "opacity": 0.2, "width": 1 },
        "move": { "enable": true, "speed": 2, "direction": "none", "random": false, "straight": false, "out_mode": "out", "bounce": false }
    },
    "interactivity": {
        "detect_on": "canvas",
        "events": {
            "onhover": { "enable": true, "mode": "grab" },
            "onclick": { "enable": true, "mode": "push" },
            "resize": true
        },
        "modes": {
            "grab": { "distance": 180, "line_linked": { "opacity": 0.5 } },
            "push": { "particles_nb": 4 }
        }
    },
    "retina_detect": true
});

// ======================== Navbar scroll effect ========================
window.addEventListener('scroll', function () {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// ======================== User Type Selection ========================
const userTypeButtons = document.querySelectorAll('.user-type-btn');
const userTypeFields = document.querySelectorAll('.user-type-fields');
userTypeButtons.forEach(button => {
    button.addEventListener('click', function () {
        userTypeButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
        const userType = this.getAttribute('data-type');
        userTypeFields.forEach(field => field.classList.add('d-none'));
        document.querySelectorAll(`.user-type-fields[data-type="${userType}"]`).forEach(field => {
            field.classList.remove('d-none');
        });
    });
});

// ======================== Search Tabs ========================
const searchTabs = document.querySelectorAll('.search-tab');
searchTabs.forEach(tab => {
    tab.addEventListener('click', function () {
        searchTabs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        console.log(`Switched to ${this.getAttribute('data-tab')} tab`);
    });
});

// ======================== Upload Functionality ========================
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');

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
            window.location.href = "/choice_login/?next=/upload_record";
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
            window.location.href = "/choice_login/?next=/upload_record";
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
        fetch('/upload_medical_data/', {
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
            const chatbotContainer = document.getElementById('chatbotContainer');
            if (chatbotContainer?.classList.contains('show')) {
                setTimeout(() => addBotMessage(`I see you've uploaded ${fileName}. Our AI is analyzing it and will add it to your health timeline.`), 1000);
            }
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
    uploadArea.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 4000);
}

// ======================== Chatbot ========================
function addBotMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    const botMessageDiv = document.createElement('div');
    botMessageDiv.className = 'message bot-message';
    botMessageDiv.textContent = text;
    chatMessages.appendChild(botMessageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addUserMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user-message';
    userMessageDiv.textContent = text;
    chatMessages.appendChild(userMessageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

const chatbotToggle = document.getElementById('chatbotToggle');
const chatbotClose = document.getElementById('chatbotClose');
const sendBtn = document.getElementById('sendBtn');
const userInput = document.getElementById('userInput');

if (chatbotToggle) {
    chatbotToggle.addEventListener('click', () => {
        const container = document.getElementById('chatbotContainer');
        container.classList.toggle('show');
        if (container.classList.contains('show')) {
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages && chatMessages.children.length === 1) {
                setTimeout(() => addBotMessage("You can ask me about uploading medical data, booking appointments, finding doctors, understanding account types (patient, doctor, hospital), security features, or anything else about MediFutura. I'm here to help!"), 1000);
            }
        }
    });
}

if (chatbotClose) {
    chatbotClose.addEventListener('click', () => document.getElementById('chatbotContainer').classList.remove('show'));
}

if (sendBtn) sendBtn.addEventListener('click', sendMessage);
if (userInput) userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

// Chatbot response logic
function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    addUserMessage(message);
    userInput.value = '';

    setTimeout(() => {
        let botResponse = "";
        const lowerMsg = message.toLowerCase();

        if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) {
            botResponse = "Hello! Great to see you. How can I assist you with MediFutura today?";
        } else if (lowerMsg.includes('help')) {
            botResponse = "I can help you with: uploading medical records, booking appointments, finding doctors or hospitals, understanding account types (patient, doctor, hospital), security features, or using our platform. What do you need help with?";
        } else if (lowerMsg.includes('upload') || lowerMsg.includes('data') || lowerMsg.includes('record')) {
            botResponse = "To upload medical data, go to the 'Upload Data' section. You can drag and drop files or click 'Browse Files' to select from your device. We support PDF, JPG, PNG, DICOM, HL7, and XML formats.";
        } else if (lowerMsg.includes('book') || lowerMsg.includes('appointment')) {
            botResponse = "To book an appointment, click on 'Book Appointments' in the navigation menu. You can search for doctors by specialty, location, and availability.";
        } else if (lowerMsg.includes('find') && (lowerMsg.includes('doctor') || lowerMsg.includes('physician'))) {
            botResponse = "You can find doctors by clicking 'Book Appointments' in the menu, then using the search filters to find doctors by specialty, location, availability, and patient ratings.";
        } else if (lowerMsg.includes('find') && (lowerMsg.includes('hospital') || lowerMsg.includes('clinic'))) {
            botResponse = "To find hospitals, click 'Book Appointments' and switch to the 'Find Hospitals' tab. You can search by location, services offered, insurance accepted, and patient ratings.";
        } else if (lowerMsg.includes('patient') || lowerMsg.includes('user')) {
            botResponse = "Patient accounts allow you to upload and store medical records, book appointments, search for doctors and hospitals, receive AI health insights, set medication reminders, and securely share information.";
        } else if (lowerMsg.includes('doctor') && !lowerMsg.includes('find')) {
            botResponse = "Doctor accounts include a digital appointment calendar, patient record access (with permission), telemedicine integration, e-prescription system, billing tools, and a patient communication portal.";
        } else if (lowerMsg.includes('hospital') && !lowerMsg.includes('find')) {
            botResponse = "Hospital accounts provide department management, staff scheduling, patient admission/discharge systems, inventory tracking, analytics dashboards, and inter-hospital collaboration tools.";
        } else if (lowerMsg.includes('register') || lowerMsg.includes('sign up') || lowerMsg.includes('create account')) {
            botResponse = "To register, click the Login/Register button and select your user type (Patient, Doctor, or Hospital). Each type has specific registration requirements.";
        } else if (lowerMsg.includes('security') || lowerMsg.includes('safe') || lowerMsg.includes('protect')) {
            botResponse = "Your data is protected with quantum encryption and blockchain verification. We use zero-knowledge architecture and role-based access control.";
        } else if (lowerMsg.includes('thank')) {
            botResponse = "You're very welcome! I'm here anytime you need assistance with MediFutura. Have a great day!";
        } else {
            botResponse = "I'm here to help with any questions about MediFutura. You might want to ask about:\n- Uploading medical records\n- Booking appointments\n- Finding hospitals\n- Account types\n- Security features\nWhat would you like to know?";
        }

        addBotMessage(botResponse);
    }, 1000);
}

// ======================== Appointment Buttons ========================
const bookButtons = document.querySelectorAll('.book-btn');
bookButtons.forEach(button => {
    button.addEventListener('click', function () {
        alert('Appointment booking would open here in the full app.');
        const chatbotContainer = document.getElementById('chatbotContainer');
        if (chatbotContainer?.classList.contains('show')) addBotMessage("I see you're interested in booking an appointment! In the full application, you would be able to select a date and time that works for you.");
    });
});

// ======================== Login Form ========================
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const activeUserType = document.querySelector('.user-type-btn.active').getAttribute('data-type');
        let email, password;
        if (activeUserType === 'patient') email = document.getElementById('email')?.value;
        else if (activeUserType === 'doctor') email = document.getElementById('doctorEmail')?.value;
        else email = document.getElementById('hospitalEmail')?.value;
        password = document.getElementById('password')?.value;

        if (email && password) {
            showAlert(`${activeUserType.charAt(0).toUpperCase() + activeUserType.slice(1)} login successful! Redirecting...`, 'success', loginForm);
            setTimeout(() => {
                window.location.href = '#dashboard';
                setTimeout(() => {
                    if (document.getElementById('chatbotContainer')?.classList.contains('show')) addBotMessage(`Welcome back, ${activeUserType}! How can I assist you with your dashboard today?`);
                }, 1500);
            }, 2000);
        } else {
            showAlert('Please fill in all required fields.', 'danger', loginForm);
        }
    });
}

function showAlert(message, type='success', parentNode=uploadArea) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} mt-3`;
    alertDiv.innerHTML = `<i class="fas fa-${type==='success'?'check-circle':'exclamation-circle'} me-2"></i> ${message}`;
    alertDiv.style.textAlign = 'center';
    alertDiv.style.fontSize = '0.9rem';
    parentNode.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 4000);
}

// ======================== Security Lock/Unlock ========================
const lockIcon = document.getElementById('lockIcon');
const unlockBtn = document.getElementById('unlockBtn');
const securityKey = document.getElementById('securityKey');

if (unlockBtn) {
    unlockBtn.addEventListener('click', () => {
        const key = securityKey.value.trim();
        if (key.length >= 6) {
            lockIcon.classList.add('unlocked');
            lockIcon.classList.remove('fa-lock');
            lockIcon.classList.add('fa-unlock');
            showAlert('Access granted! Your medical data is now available.', 'success', unlockBtn.parentNode);
            if (document.getElementById('chatbotContainer')?.classList.contains('show')) setTimeout(() => addBotMessage("Great! You've successfully unlocked your medical data. You can now view your records, upload new documents, or book appointments."), 1500);
        } else {
            showAlert('Please enter a valid 6-8 digit security key.', 'danger', unlockBtn.parentNode);
            lockIcon.style.animation = 'shake 0.5s';
            setTimeout(() => lockIcon.style.animation = '', 500);
        }
    });
}

const style = document.createElement('style');
style.textContent = `@keyframes shake {0%,100%{transform:translateX(0);}10%,30%,50%,70%,90%{transform:translateX(-5px);}20%,40%,60%,80%{transform:translateX(5px);}}`;
document.head.appendChild(style);

if (securityKey) {
    securityKey.addEventListener('input', () => {
        if (securityKey.value === '') {
            lockIcon.classList.remove('unlocked');
            lockIcon.classList.remove('fa-unlock');
            lockIcon.classList.add('fa-lock');
        }
    });
}

// ======================== Stats Counter ========================
function animateCounter(elementId, target, duration) {
    const element = document.getElementById(elementId);
    if (!element) return;
    let start = 0;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            clearInterval(timer);
            element.textContent = Math.floor(target) + '+';
        } else element.textContent = Math.floor(start) + '+';
    }, 16);
}

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounter('userCount', 25000, 2500);
            animateCounter('doctorCount', 2500, 2000);
            animateCounter('hospitalCount', 500, 2000);
            observer.disconnect();
        }
    });
}, { threshold: 0.5 });

const statsSection = document.getElementById('stats');
if (statsSection) observer.observe(statsSection);

// ======================== Smooth Scroll ========================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href'))?.scrollIntoView({ behavior: 'smooth' });
    });
});

// ======================== Floating Animation ========================
const floatingElements = document.querySelectorAll('.floating');
floatingElements.forEach(el => {
    const amplitude = parseInt(el.getAttribute('data-amplitude')) || 10;
    const speed = parseFloat(el.getAttribute('data-speed')) || 0.002;
    let angle = 0;
    function float() {
        angle += speed * Math.PI * 2;
        el.style.transform = `translateY(${Math.sin(angle) * amplitude}px)`;
        requestAnimationFrame(float);
    }
    float();
});
