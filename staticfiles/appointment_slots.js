function logFormSubmit() {
  console.log("Add Slot form submitted at", new Date().toISOString());
}

function logButtonClick(buttonName) {
  console.log(`${buttonName} button clicked at ${new Date().toISOString()}`);
}

document.getElementById('slot-form').addEventListener('submit', function(event) {
  const date = document.getElementById('slot-date').value;
  const time = document.getElementById('slot-time').value;
  const duration = document.getElementById('slot-duration').value;
  if (!date || !time || !duration) {
    event.preventDefault();
    alert('Please fill in all required fields.');
  }
});

// Debug session data
console.log("Doctor Name:", "{{ request.session.doctor_name|default:'Not set' }}");
