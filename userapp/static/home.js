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

// ======================== Search Tabs Functionality - SIMPLIFIED ========================
document.addEventListener('DOMContentLoaded', function() {
    const searchTabs = document.querySelectorAll('.search-tab');
    const typeInput = document.getElementById('typeInput');
    const specialtyInput = document.getElementById('specialtyInput');
    
    // Tab switching functionality - ONLY updates the form fields
    searchTabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent any default behavior
            
            // Remove active class from all tabs
            searchTabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Update search type based on selected tab
            const tabType = this.getAttribute('data-tab');
            updateSearchType(tabType);
        });
    });

    function updateSearchType(tabType) {
        switch(tabType) {
            case 'doctors':
                if (typeInput) typeInput.value = 'doctors';
                if (specialtyInput) specialtyInput.disabled = false;
                break;
            case 'hospitals':
                if (typeInput) typeInput.value = 'hospitals';
                if (specialtyInput) {
                    specialtyInput.disabled = true;
                    specialtyInput.value = '';
                }
                break;
            case 'specialties':
                if (typeInput) typeInput.value = 'doctors';
                if (specialtyInput) specialtyInput.disabled = false;
                break;
        }
    }

    // Initialize based on current URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const currentType = urlParams.get('search_type');
    if (currentType === 'hospitals' && searchTabs.length > 0) {
        // Activate hospitals tab
        searchTabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === 'hospitals') {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
    }
});

// ======================== COMPLETELY REMOVE SEARCH FORM JAVASCRIPT INTERFERENCE ========================
// Remove any event listeners that might be interfering with the search form
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        // Completely replace the form to remove any attached event listeners
        const newForm = searchForm.cloneNode(true);
        searchForm.parentNode.replaceChild(newForm, searchForm);
        
        console.log('Search form cleaned - will submit naturally to home page');
    }
});

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