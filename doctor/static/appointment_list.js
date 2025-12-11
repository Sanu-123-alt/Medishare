
function toggleTheme() {
  const body = document.body;
  const currentTheme = body.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  body.setAttribute('data-theme', newTheme);
  const icon = document.querySelector('.theme-toggle i');
  icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

function logButtonClick(buttonName) {
  console.log(`${buttonName} button clicked at ${new Date().toISOString()}`);
}

// Debug session data
console.log("Doctor Name:", "{{ request.session.doctor_name|default:'Not set' }}");
