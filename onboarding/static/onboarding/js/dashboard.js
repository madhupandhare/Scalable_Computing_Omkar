const studentId = localStorage.getItem('studentId');
const studentCountry = localStorage.getItem('studentCountry');

const profileEl = document.getElementById('studentProfile');
const countryEl = document.getElementById('countryInfo');
const restaurantsEl = document.getElementById('restaurantResults');
const restaurantForm = document.getElementById('restaurantForm');
const dashboardAlert = document.getElementById('dashboardAlert');

if (!studentId) {
  dashboardAlert.innerHTML = '<div class="alert alert-warning">No active student session found. Please register first.</div>';
}

async function loadStudent() {
  const response = await fetch(`/api/student/${studentId}`);
  const student = await response.json();
  if (!response.ok) {
    throw new Error('Unable to load student profile');
  }

  profileEl.innerHTML = `
    <li class="list-group-item"><strong>Full Name:</strong> ${student.full_name}</li>
    <li class="list-group-item"><strong>Email:</strong> ${student.email}</li>
    <li class="list-group-item"><strong>Phone:</strong> ${student.phone}</li>
    <li class="list-group-item"><strong>Card ID:</strong> ${student.card_id}</li>
  `;
}

async function loadCountryInfo() {
  const response = await fetch(`/api/country-info?country=${encodeURIComponent(studentCountry)}`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error('Unable to load country info');
  }

  countryEl.innerHTML = `
    <p class="mb-1"><strong>Country:</strong> ${data.country}</p>
    <p class="mb-1"><strong>Currency:</strong> ${data.currency_name} (${data.currency}) ${data.currency_symbol}</p>
    <p class="mb-1"><strong>Timezone:</strong> ${data.timezone}</p>
    <p class="mb-1"><strong>Calling Code:</strong> ${data.calling_code}</p>
    <p class="mb-1"><strong>Region:</strong> ${data.region}</p>
    ${data.flag ? `<img src="${data.flag}" alt="Flag" class="img-fluid mt-2" style="max-height: 80px;">` : ''}
  `;
}

restaurantForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(restaurantForm);
  const payload = Object.fromEntries(formData.entries());
  payload.student_id = studentId;

  const response = await fetch('/api/get-restaurants', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    restaurantsEl.innerHTML = '<div class="col-12"><div class="alert alert-danger">Unable to fetch restaurant suggestions.</div></div>';
    return;
  }

  restaurantsEl.innerHTML = data.restaurants.map((restaurant) => `
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <h3 class="h6">${restaurant.name || 'Unnamed restaurant'}</h3>
            <p class="mb-1"><strong>City:</strong> ${restaurant.city || data.campus_city}</p>
            <p class="mb-1"><strong>Budget:</strong> ${restaurant.budget || payload.budget}</p>
            <p class="mb-1"><strong>Rating:</strong> ${restaurant.rating || 'N/A'}</p>
            <p class="text-muted small">${restaurant.note || ''}</p>
          </div>
        </div>
      </div>
    `).join('');
});

(async () => {
  if (!studentId || !studentCountry) {
    return;
  }

  try {
    await loadStudent();
    await loadCountryInfo();
  } catch (error) {
    dashboardAlert.innerHTML = '<div class="alert alert-danger">Failed to load dashboard data.</div>';
  }
})();
