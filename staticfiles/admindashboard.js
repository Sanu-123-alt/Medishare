// Ensure DOM is fully loaded before running scripts
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM fully loaded, initializing scripts...');

  // ---------- Sidebar mobile toggle ----------
  const mobileToggle = document.getElementById('mobileToggle');
  const sidebar = document.getElementById('sidebar');
  const main = document.getElementById('main');

  if (!mobileToggle || !sidebar || !main) {
    console.error('Sidebar elements missing:', { mobileToggle, sidebar, main });
    return;
  }

  mobileToggle.addEventListener('click', () => {
    console.log('Mobile toggle clicked');
    sidebar.classList.toggle('show');
  });

  main.addEventListener('click', (e) => {
    if (window.innerWidth <= 760 && sidebar.classList.contains('show')) {
      console.log('Closing sidebar on main click');
      sidebar.classList.remove('show');
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
      themeIcon.className = 'bi bi-sun';
    } else {
      document.body.classList.remove('dark');
      document.body.classList.add('light');
      themeIcon.className = 'bi bi-moon';
    }
    try {
      localStorage.setItem('medishare-theme', mode);
    } catch (err) {
      console.warn('Failed to save theme to localStorage:', err);
    }
  }

  // Initialize theme based on localStorage or system preference
  const savedTheme = localStorage.getItem('medishare-theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(savedTheme);

  themeToggle.addEventListener('click', () => {
    console.log('Theme toggle clicked');
    const isDark = document.body.classList.contains('dark');
    applyTheme(isDark ? 'light' : 'dark');
  });

  // ---------- Charts ----------
  function createGradient(ctx, color1, color2) {
    const g = ctx.createLinearGradient(0, 0, 0, 350);
    g.addColorStop(0, color1);
    g.addColorStop(1, color2);
    return g;
  }

  const userCtx = document.getElementById('userChart')?.getContext('2d');
  if (userCtx) {
    try {
      const g1 = createGradient(userCtx, 'rgba(59, 130, 246, 0.35)', 'rgba(139, 92, 246, 0.05)');
      new Chart(userCtx, {
        type: 'line',
        data: {
          labels: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
          datasets: [{
            label: 'New Users',
            data: [150, 320, 540, 700, 980, 1250],
            fill: true,
            backgroundColor: g1,
            borderColor: '#3b82f6',
            tension: 0.36,
            pointRadius: 3
          }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
      });
      console.log('User chart initialized');
    } catch (err) {
      console.error('Failed to initialize user chart:', err);
    }
  } else {
    console.warn('User chart canvas not found');
  }

  const donutCtx = document.getElementById('donutChart')?.getContext('2d');
  if (donutCtx) {
    try {
      new Chart(donutCtx, {
        type: 'doughnut',
        data: {
          labels: ['Diabetes', 'Cancer', 'Other'],
          datasets: [{
            data: [1200, 800, 2560],
            backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
      });
      console.log('Donut chart initialized');
    } catch (err) {
      console.error('Failed to initialize donut chart:', err);
    }
  } else {
    console.warn('Donut chart canvas not found');
  }

  // ---------- Table operations ----------
  const hospitalTable = document.getElementById('hospitalTable')?.querySelector('tbody');
  const tableCount = document.getElementById('tableCount');

  if (!hospitalTable || !tableCount) {
    console.error('Hospital table elements missing:', { hospitalTable, tableCount });
    return;
  }

  function updateTableCount() {
    tableCount.textContent = hospitalTable.querySelectorAll('tr').length;
    console.log('Table count updated:', tableCount.textContent);
  }
  updateTableCount();

  hospitalTable.addEventListener('click', (e) => {
    if (e.target.closest('.delBtn')) {
      const tr = e.target.closest('tr');
      if (confirm('Delete this hospital?')) {
        console.log('Deleting hospital row:', tr.children[0].textContent);
        tr.remove();
        updateTableCount();
      }
    }
    if (e.target.closest('.editBtn')) {
      const tr = e.target.closest('tr');
      const cells = tr.children;
      console.log('Editing hospital:', cells[0].textContent);
      const hName = document.getElementById('hName');
      const hLocation = document.getElementById('hLocation');
      const hCategory = document.getElementById('hCategory');
      const hDoctors = document.getElementById('hDoctors');
      if (hName && hLocation && hCategory && hDoctors) {
        hName.value = cells[0].textContent;
        hLocation.value = cells[1].textContent;
        hCategory.value = cells[2].textContent;
        hDoctors.value = cells[3].textContent;
        openHospitalForm();
        document.getElementById('hospitalForm').dataset.editId = tr.dataset.id || '';
      } else {
        console.error('Hospital form inputs missing');
      }
    }
  });

  // ---------- Hospital form show/hide ----------
  const openHospitalFormBtn = document.getElementById('openHospitalForm');
  const hospitalFormCard = document.getElementById('hospitalFormCard');
  const closeHospitalFormBtn = document.getElementById('closeHospitalForm');

  if (!openHospitalFormBtn || !hospitalFormCard || !closeHospitalFormBtn) {
    console.error('Hospital form elements missing:', { openHospitalFormBtn, hospitalFormCard, closeHospitalFormBtn });
    return;
  }

  function openHospitalForm() {
    console.log('Opening hospital form');
    hospitalFormCard.style.display = 'block';
    hospitalFormCard.scrollIntoView({ behavior: 'smooth' });
  }

  function closeHospitalForm() {
    console.log('Closing hospital form');
    hospitalFormCard.style.display = 'none';
    const hospitalForm = document.getElementById('hospitalForm');
    if (hospitalForm) {
      hospitalForm.reset();
      delete hospitalForm.dataset.editId;
    }
  }

  openHospitalFormBtn.addEventListener('click', () => {
    console.log('Add Hospital button clicked');
    openHospitalForm();
  });

  closeHospitalFormBtn.addEventListener('click', closeHospitalForm);

  document.getElementById('resetHospitalForm')?.addEventListener('click', () => {
    console.log('Resetting hospital form');
    const hospitalForm = document.getElementById('hospitalForm');
    if (hospitalForm) {
      hospitalForm.reset();
      delete hospitalForm.dataset.editId;
    }
  });

  document.getElementById('hospitalForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    console.log('Hospital form submitted');
    const name = document.getElementById('hName')?.value.trim();
    const location = document.getElementById('hLocation')?.value.trim();
    const category = document.getElementById('hCategory')?.value;
    const doctors = document.getElementById('hDoctors')?.value || '0';

    if (!name || !location || !category) {
      console.error('Hospital form inputs missing or invalid');
      return;
    }

    const editId = e.target.dataset.editId;
    if (editId) {
      const tr = hospitalTable.querySelector(`tr[data-id="${editId}"]`);
      if (tr) {
        console.log('Updating hospital:', name);
        tr.children[0].textContent = name;
        tr.children[1].textContent = location;
        tr.children[2].textContent = category;
        tr.children[3].textContent = doctors;
      }
    } else {
      const newId = Date.now();
      const tr = document.createElement('tr');
      tr.dataset.id = newId;
      tr.innerHTML = `<td>${name}</td><td>${location}</td><td>${category}</td><td>${doctors}</td>
        <td>
          <button class="action-btn editBtn" title="Edit"><i class="bi bi-pencil-square"></i></button>
          <button class="action-btn delBtn" title="Delete"><i class="bi bi-trash"></i></button>
        </td>`;
      hospitalTable.prepend(tr);
      console.log('Added new hospital:', name);
      updateTableCount();
    }

    e.target.reset();
    delete e.target.dataset.editId;
    hospitalFormCard.style.display = 'none';
  });

  // ---------- Doctor form show/hide ----------
  const openDoctorFormBtn = document.getElementById('openDoctorForm');
  const doctorFormCard = document.getElementById('doctorFormCard');
  const closeDoctorFormBtn = document.getElementById('closeDoctorForm');

  if (!openDoctorFormBtn || !doctorFormCard || !closeDoctorFormBtn) {
    console.error('Doctor form elements missing:', { openDoctorFormBtn, doctorFormCard, closeDoctorFormBtn });
    return;
  }

  openDoctorFormBtn.addEventListener('click', () => {
    console.log('Add Doctor button clicked');
    doctorFormCard.style.display = 'block';
    doctorFormCard.scrollIntoView({ behavior: 'smooth' });
  });

  closeDoctorFormBtn.addEventListener('click', () => {
    console.log('Closing doctor form');
    doctorFormCard.style.display = 'none';
    const doctorForm = document.getElementById('doctorForm');
    if (doctorForm) doctorForm.reset();
  });

  document.getElementById('doctorForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    console.log('Doctor form submitted');
    alert('Doctor added (demo). Implement server-side to persist.');
    e.target.reset();
    doctorFormCard.style.display = 'none';
  });

  document.getElementById('resetDoctorForm')?.addEventListener('click', () => {
    console.log('Resetting doctor form');
    const doctorForm = document.getElementById('doctorForm');
    if (doctorForm) doctorForm.reset();
  });

  // ---------- Import Users button (placeholder) ----------
  const openUserImportBtn = document.getElementById('openUserImport');
  if (openUserImportBtn) {
    openUserImportBtn.addEventListener('click', () => {
      console.log('Import Users button clicked');
      alert('Import Users (demo). Implement server-side to persist.');
    });
  } else {
    console.error('Import Users button missing');
  }

  // ---------- Search table (simple) ----------
  const searchBox = document.getElementById('searchBox');
  if (searchBox) {
    searchBox.addEventListener('input', (e) => {
      console.log('Search input:', e.target.value);
      const q = e.target.value.toLowerCase();
      document.querySelectorAll('#hospitalTable tbody tr').forEach(tr => {
        const txt = tr.textContent.toLowerCase();
        tr.style.display = txt.includes(q) ? '' : 'none';
      });
    });
  } else {
    console.error('Search box missing');
  }

  // ---------- Init: adjust sidebar for screen size ----------
  function adjustSidebar() {
    if (window.innerWidth <= 760) {
      sidebar.classList.remove('show');
      console.log('Sidebar hidden for mobile');
    }
  }
  window.addEventListener('resize', adjustSidebar);
  adjustSidebar();

  // ---------- Dynamic stats update based on table content ----------
  function refreshStatsFromTable() {
    const statHosp = document.getElementById('statHosp');
    if (statHosp) {
      statHosp.textContent = hospitalTable.querySelectorAll('tr').length;
      console.log('Hospital stats updated:', statHosp.textContent);
    }
    updateTableCount();
  }
  refreshStatsFromTable();
});