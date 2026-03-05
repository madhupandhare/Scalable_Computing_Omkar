const registerForm = document.getElementById('registerForm');
const registerAlert = document.getElementById('registerAlert');

registerForm?.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(registerForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch('/api/register-student', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      registerAlert.innerHTML = `<div class="alert alert-danger">Could not register student. ${JSON.stringify(data.errors || data.error)}</div>`;
      return;
    }

    localStorage.setItem('studentId', data.student.id);
    localStorage.setItem('studentCountry', data.student.home_country);
    registerAlert.innerHTML = '<div class="alert alert-success">Registration complete. Redirecting to dashboard...</div>';
    window.setTimeout(() => {
      window.location.href = '/dashboard/';
    }, 700);
  } catch (error) {
    registerAlert.innerHTML = '<div class="alert alert-danger">Network error. Please try again.</div>';
  }
});
