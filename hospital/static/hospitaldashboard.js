document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM fully loaded, initializing MediShare dashboard...');

  // ---------- Sidebar mobile toggle ----------
  const mobileToggle = document.getElementById('mobileToggle');
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.querySelector('.main-content');

  if (!mobileToggle || !sidebar || !mainContent) {
    console.error('Sidebar elements missing:', { mobileToggle, sidebar, mainContent });
    return;
  }

  mobileToggle.addEventListener('click', () => {
    console.log('Mobile toggle clicked');
    sidebar.classList.toggle('active');
  });

  mainContent.addEventListener('click', () => {
    if (window.innerWidth <= 600 && sidebar.classList.contains('active')) {
      console.log('Closing sidebar on main content click');
      sidebar.classList.remove('active');
    }
  });

  // ---------- Theme toggle with persistence ----------
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon = document.getElementById('themeIcon');

  if (!themeToggle || !themeIcon) {
    console.error('Theme toggle elements missing:', { themeToggle, themeIcon });
    return;
  }

  function applyTheme(mode) {
    console.log(`Applying theme: ${mode}`);
    if (mode === 'dark') {
      document.body.classList.add('dark');
      document.body.classList.remove('light');
      themeIcon.className = 'fas fa-sun';
    } else {
      document.body.classList.add('light');
      document.body.classList.remove('dark');
      themeIcon.className = 'fas fa-moon';
    }
    try {
      localStorage.setItem('medishare-theme', mode);
    } catch (err) {
      console.warn('Failed to save theme to localStorage:', err);
    }
  }

  // Initialize theme
  const savedTheme = localStorage.getItem('medishare-theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(savedTheme);

  themeToggle.addEventListener('click', () => {
    console.log('Theme toggle clicked');
    const isDark = document.body.classList.contains('dark');
    applyTheme(isDark ? 'light' : 'dark');
  });

  // ---------- Quick actions, activity log, and system status ----------
  const activityLog = document.getElementById('activityLog');
  const statDoctors = document.getElementById('statDoctors');
  const statPatients = document.getElementById('statPatients');
  const statUsers = document.getElementById('statUsers');
  const statAppointments = document.getElementById('statAppointments');
  const activeUsers = document.getElementById('activeUsers');
  const pendingTasks = document.getElementById('pendingTasks');
  const appointmentTable = document.getElementById('appointmentTable');

  if (!activityLog || !statDoctors || !statPatients || !statUsers || !statAppointments || !activeUsers || !pendingTasks || !appointmentTable) {
    console.error('Critical elements missing:', { activityLog, statDoctors, statPatients, statUsers, statAppointments, activeUsers, pendingTasks, appointmentTable });
    return;
  }

  // Initialize activity log with sample data
  const initialActivities = [
    { action: 'Added Doctor: Dr. Smith', timestamp: '2025-09-17 10:30 AM' },
    { action: 'Added Patient: John Doe', timestamp: '2025-09-17 09:15 AM' },
    { action: 'Scheduled Appointment', timestamp: '2025-09-16 04:20 PM' }
  ];

  function addActivity(action) {
    const timestamp = new Date().toLocaleString('en-US', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
    const li = document.createElement('li');
    li.textContent = `${action} at ${timestamp}`;
    activityLog.prepend(li);
    console.log(`Activity added: ${action} at ${timestamp}`);
  }

  // Populate initial activities
  initialActivities.forEach(activity => {
    const li = document.createElement('li');
    li.textContent = `${activity.action} at ${activity.timestamp}`;
    activityLog.appendChild(li);
  });

  // Update system stats and appointments
  function updateStatsAndAppointments(actionType) {
    if (actionType === 'Doctor') {
      statDoctors.textContent = parseInt(statDoctors.textContent) + 1;
      console.log('Updated Doctors stat:', statDoctors.textContent);
    } else if (actionType === 'Patient') {
      statPatients.textContent = parseInt(statPatients.textContent) + 1;
      console.log('Updated Patients stat:', statPatients.textContent);
    } else if (actionType === 'User') {
      statUsers.textContent = parseInt(statUsers.textContent) + 1;
      activeUsers.textContent = parseInt(activeUsers.textContent) + 1;
      console.log('Updated Users and Active Users stats:', statUsers.textContent, activeUsers.textContent);
    } else if (actionType === 'Appointment') {
      statAppointments.textContent = parseInt(statAppointments.textContent) + 1;
      pendingTasks.textContent = parseInt(pendingTasks.textContent) + 1;
      const newId = `A${(parseInt(appointmentTable.querySelectorAll('tr').length) + 1).toString().padStart(3, '0')}`;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${newId}</td>
        <td>New Patient</td>
        <td>Dr. Unknown</td>
        <td>${new Date().toLocaleDateString('en-CA')}</td>
        <td><span class="status pending">Pending</span></td>
      `;
      appointmentTable.prepend(tr);
      console.log('Updated Appointments stat and table:', statAppointments.textContent);
    }
  }

  const actionButtons = {
    addDoctor: document.getElementById('addDoctor'),
    addPatient: document.getElementById('addPatient'),
    addUser: document.getElementById('addUser'),
    addAppointment: document.getElementById('addAppointment')
  };

  Object.entries(actionButtons).forEach(([key, button]) => {
    if (!button) {
      console.error(`Quick action button missing: ${key}`);
      return;
    }
    button.addEventListener('click', () => {
      console.log(`${key} button clicked`);
      const actionText = key.replace('add', 'Added ').replace(/([A-Z])/g, ' $1').trim();
      const actionType = key.replace('add', '');
      addActivity(actionText);
      updateStatsAndAppointments(actionType);
      alert(`${actionText} (demo). Implement server-side to persist.`);
    });
  });
});