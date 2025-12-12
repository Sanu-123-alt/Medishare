function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('active');
}

function logButtonClick(buttonName) {
  console.log(`${buttonName} button clicked at ${new Date().toISOString()}`);
}
console.log("Doctor Image URL:", "{{ request.session.doctor_image.url|default:'Not set' }}");
console.log("Doctor Name:", "{{ request.session.doctor_name|default:'Not set' }}");
